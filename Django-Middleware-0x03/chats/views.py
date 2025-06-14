from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, 
    ConversationSerializer, 
    ConversationListSerializer,
    MessageSerializer
)
from .permissions import (
    IsOwnerOrReadOnly,
    IsParticipantOrReadOnly,
    IsParticipantOfConversation,
    IsMessageSenderOrParticipant,
    CanAccessOwnDataOnly
)
from .pagination import (
    MessagePagination,
    ConversationPagination,
    StandardResultsSetPagination
)
from .filters import (
    MessageFilter,
    ConversationFilter,
    UserFilter
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    Provides CRUD operations for user management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'created_at', 'is_online']
    ordering = ['username']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Filter users based on query parameters"""
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset.exclude(user_id=self.request.user.user_id)  # Exclude current user


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations.
    Provides endpoints to list, create, and manage conversations.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ConversationFilter
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    pagination_class = ConversationPagination

    def get_queryset(self):
        """Return conversations where the current user is a participant"""
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related('participants', 'messages__sender')

    def get_serializer_class(self):
        """Use different serializers for list vs detail views"""
        if self.action == 'list':
            return ConversationListSerializer
        return ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation.
        Automatically adds the request user as a participant.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save()
        
        # Return the conversation with full details
        response_serializer = ConversationSerializer(conversation, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """Add a participant to an existing conversation"""
        conversation = self.get_object()
        
        # Check if user is a participant in the conversation
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to add participants to this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
            return Response(
                {'message': f'User {user.username} added to conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """Remove a participant from a conversation"""
        conversation = self.get_object()
        
        # Check if user is a participant in the conversation
        if request.user not in conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to remove participants from this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(user_id=user_id)
            conversation.participants.remove(user)
            return Response(
                {'message': f'User {user.username} removed from conversation'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages.
    Provides endpoints to list, create, and manage messages within conversations.
    Implements pagination (20 messages per page) and filtering capabilities.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['message_body', 'sender__username']
    ordering_fields = ['timestamp', 'sent_at', 'is_read']
    ordering = ['-timestamp']
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        Return messages from conversations where the user is a participant.
        Can be filtered by conversation_id.
        """
        queryset = Message.objects.filter(
            conversation__participants=self.request.user
        ).select_related('sender', 'conversation')
        
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a new message.
        Automatically sets the sender to the request user.
        """
        # Ensure the user is a participant in the conversation
        conversation_id = request.data.get('conversation')
        if conversation_id:
            try:
                conversation = Conversation.objects.get(
                    conversation_id=conversation_id
                )
                # Check if user is a participant
                if request.user not in conversation.participants.all():
                    return Response(
                        {'error': 'You are not authorized to send messages to this conversation'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Conversation.DoesNotExist:
                return Response(
                    {'error': 'Conversation not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender=request.user)
        
        return Response(
            MessageSerializer(message).data, 
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, pk=None):
        """Mark a message as read"""
        message = self.get_object()
        message.is_read = True
        message.save()
        
        return Response(
            {'message': 'Message marked as read'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'])
    def mark_conversation_as_read(self, request):
        """Mark all messages in a conversation as read"""
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(
                conversation_id=conversation_id,
                participants=request.user
            )
            
            # Mark all messages as read for this user
            Message.objects.filter(
                conversation=conversation
            ).exclude(sender=request.user).update(is_read=True)
            
            return Response(
                {'message': 'All messages in conversation marked as read'},
                status=status.HTTP_200_OK
            )
            
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found or you are not a participant'},
                status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        """
        Update a message. Only the sender can update their own messages.
        """
        message = self.get_object()
        
        # Check if user is the sender of the message
        if message.sender != request.user:
            return Response(
                {'error': 'You are not authorized to update this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is still a participant in the conversation
        if request.user not in message.conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to update messages in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(message, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a message. Only the sender can delete their own messages.
        """
        message = self.get_object()
        
        # Check if user is the sender of the message
        if message.sender != request.user:
            return Response(
                {'error': 'You are not authorized to delete this message'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if user is still a participant in the conversation
        if request.user not in message.conversation.participants.all():
            return Response(
                {'error': 'You are not authorized to delete messages in this conversation'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.delete()
        return Response(
            {'message': 'Message deleted successfully'},
            status=status.HTTP_204_NO_CONTENT
        )
