import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters
from .models import Message, Conversation, User


class MessageFilter(django_filters.FilterSet):
    """
    Filter class for messages to retrieve conversations with specific users 
    or messages within a time range
    """
    # Time range filters
    start_date = django_filters.DateTimeFilter(
        field_name='timestamp', 
        lookup_expr='gte',
        help_text='Filter messages from this date and time (YYYY-MM-DD HH:MM:SS)'
    )
    end_date = django_filters.DateTimeFilter(
        field_name='timestamp', 
        lookup_expr='lte',
        help_text='Filter messages up to this date and time (YYYY-MM-DD HH:MM:SS)'
    )
    
    # Date only filters (for easier use)
    date_from = django_filters.DateFilter(
        field_name='timestamp', 
        lookup_expr='date__gte',
        help_text='Filter messages from this date (YYYY-MM-DD)'
    )
    date_to = django_filters.DateFilter(
        field_name='timestamp', 
        lookup_expr='date__lte',
        help_text='Filter messages up to this date (YYYY-MM-DD)'
    )
    
    # Sender filter
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        help_text='Filter messages by sender user ID'
    )
    
    # Sender username filter (easier to use)
    sender_username = django_filters.CharFilter(
        field_name='sender__username',
        lookup_expr='icontains',
        help_text='Filter messages by sender username (case insensitive)'
    )
    
    # Conversation filter
    conversation = django_filters.ModelChoiceFilter(
        queryset=Conversation.objects.all(),
        field_name='conversation',
        help_text='Filter messages by conversation ID'
    )
    
    # Message content filter
    message_body = django_filters.CharFilter(
        field_name='message_body',
        lookup_expr='icontains',
        help_text='Search in message content (case insensitive)'
    )
    
    # Read status filter
    is_read = django_filters.BooleanFilter(
        field_name='is_read',
        help_text='Filter by read status (true/false)'
    )
    
    # Participants filter - messages from conversations with specific users
    participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        method='filter_by_participant',
        help_text='Filter messages from conversations with this participant'
    )
    
    # Participant username filter
    participant_username = django_filters.CharFilter(
        method='filter_by_participant_username',
        help_text='Filter messages from conversations with this participant username'
    )
    
    # Order by options
    ordering = django_filters.OrderingFilter(
        fields=(
            ('timestamp', 'timestamp'),
            ('sent_at', 'sent_at'),
            ('is_read', 'is_read'),
        ),
        field_labels={
            'timestamp': 'Timestamp',
            'sent_at': 'Sent At',
            'is_read': 'Read Status',
        }
    )

    class Meta:
        model = Message
        fields = [
            'start_date', 'end_date', 'date_from', 'date_to',
            'sender', 'sender_username', 'conversation', 
            'message_body', 'is_read', 'participant', 'participant_username'
        ]

    def filter_by_participant(self, queryset, name, value):
        """
        Filter messages from conversations where the specified user is a participant
        """
        if value:
            return queryset.filter(conversation__participants=value)
        return queryset

    def filter_by_participant_username(self, queryset, name, value):
        """
        Filter messages from conversations where a participant has the specified username
        """
        if value:
            return queryset.filter(conversation__participants__username__icontains=value)
        return queryset


class ConversationFilter(django_filters.FilterSet):
    """
    Filter class for conversations
    """
    # Participant filter
    participant = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='participants',
        help_text='Filter conversations by participant user ID'
    )
    
    # Participant username filter
    participant_username = django_filters.CharFilter(
        field_name='participants__username',
        lookup_expr='icontains',
        help_text='Filter conversations by participant username'
    )
    
    # Date range filters
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter conversations created after this date'
    )
    created_before = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        help_text='Filter conversations created before this date'
    )
    
    # Updated date filters
    updated_after = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='gte',
        help_text='Filter conversations updated after this date'
    )
    updated_before = django_filters.DateTimeFilter(
        field_name='updated_at',
        lookup_expr='lte',
        help_text='Filter conversations updated before this date'
    )
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('created_at', 'created_at'),
            ('updated_at', 'updated_at'),
        ),
        field_labels={
            'created_at': 'Created At',
            'updated_at': 'Updated At',
        }
    )

    class Meta:
        model = Conversation
        fields = [
            'participant', 'participant_username',
            'created_after', 'created_before',
            'updated_after', 'updated_before'
        ]


class UserFilter(django_filters.FilterSet):
    """
    Filter class for users
    """
    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains',
        help_text='Filter by username (case insensitive)'
    )
    
    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        help_text='Filter by email (case insensitive)'
    )
    
    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        help_text='Filter by first name (case insensitive)'
    )
    
    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains',
        help_text='Filter by last name (case insensitive)'
    )
    
    is_online = django_filters.BooleanFilter(
        field_name='is_online',
        help_text='Filter by online status'
    )
    
    created_after = django_filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        help_text='Filter users created after this date'
    )
    
    ordering = django_filters.OrderingFilter(
        fields=(
            ('username', 'username'),
            ('email', 'email'),
            ('created_at', 'created_at'),
            ('is_online', 'is_online'),
        )
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_online', 'created_after']
