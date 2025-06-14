from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants in a conversation to send, view, update and delete messages.
    """
    def has_permission(self, request, view):
        """
        Allow only authenticated users to access the API
        """
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Allow only participants in a conversation to send, view, update and delete messages
        """
        # For conversation objects
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
            
            # Allow GET for participants
            if request.method == 'GET':
                return is_participant
            
            # Allow POST, PUT, PATCH, DELETE for participants
            if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
                return is_participant
                
            return is_participant
        
        # For message objects, check if user is participant in the conversation
        if hasattr(obj, 'conversation'):
            is_participant = request.user in obj.conversation.participants.all()
            
            # Allow GET for participants
            if request.method == 'GET':
                return is_participant
            
            # Allow POST for participants (creating new messages)
            if request.method == 'POST':
                return is_participant
            
            # Allow PUT, PATCH, DELETE only for message sender who is also a participant
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                return is_participant and obj.sender == request.user
                
            return is_participant
        
        return False


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is a participant in the conversation
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For messages, check if user is participant in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False


class IsMessageSenderOrParticipant(permissions.BasePermission):
    """
    Custom permission for messages - allows sender to edit/delete,
    and all participants to read.
    """
    def has_object_permission(self, request, view, obj):
        # Check if user is participant in the conversation
        is_participant = request.user in obj.conversation.participants.all()
        
        if request.method in permissions.SAFE_METHODS:
            # Read permissions for participants
            return is_participant
        else:
            # Write permissions only for the sender
            return is_participant and obj.sender == request.user


class CanAccessOwnDataOnly(permissions.BasePermission):
    """
    Permission to ensure users can only access their own data.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For User objects
        if hasattr(obj, 'user_id'):
            return obj == request.user
        
        # For conversations - check if user is a participant
        if hasattr(obj, 'participants'):
            return request.user in obj.participants.all()
        
        # For messages - check if user is in the conversation
        if hasattr(obj, 'conversation'):
            return request.user in obj.conversation.participants.all()
        
        return False
