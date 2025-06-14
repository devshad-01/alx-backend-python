from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .managers import UnreadMessagesManager


class Message(models.Model):
    """
    Model to represent a message sent between users.
    Supports threaded conversations with parent-child relationships.
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text="User who sent this message"
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        help_text="User who received this message"
    )
    content = models.TextField(help_text="Message content")
    timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="When the message was sent"
    )
    edited = models.BooleanField(
        default=False,
        help_text="Whether the message has been edited"
    )
    read = models.BooleanField(
        default=False,
        help_text="Whether the message has been read by the receiver"
    )
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent message if this is a reply"
    )

    # Custom managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages
    
    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"

    @property
    def is_reply(self):
        """Check if this message is a reply to another message."""
        return self.parent_message is not None

    @property
    def is_thread_root(self):
        """Check if this message is the root of a thread."""
        return self.parent_message is None

    def get_thread_root(self):
        """Get the root message of this thread."""
        if self.is_thread_root:
            return self
        return self.parent_message.get_thread_root()

    def get_all_replies(self):
        """
        Get all replies to this message recursively using optimized queries.
        Returns a queryset of all replies in the thread.
        """
        from django.db.models import Q
        
        # Get all replies recursively
        replies = Message.objects.filter(
            parent_message=self
        ).prefetch_related(
            'sender',
            'receiver',
            'replies__sender',
            'replies__receiver'
        ).select_related('sender', 'receiver')
        
        return replies

    def get_thread_messages(self):
        """
        Get all messages in this thread (including the root and all replies).
        Returns messages organized in a hierarchical structure.
        """
        root = self.get_thread_root()
        
        # Use raw SQL for recursive query to get all thread messages
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE thread_messages AS (
                    -- Base case: root message
                    SELECT id, sender_id, receiver_id, content, timestamp, edited, parent_message_id, 0 as level
                    FROM messaging_message 
                    WHERE id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: replies
                    SELECT m.id, m.sender_id, m.receiver_id, m.content, m.timestamp, m.edited, m.parent_message_id, tm.level + 1
                    FROM messaging_message m
                    INNER JOIN thread_messages tm ON m.parent_message_id = tm.id
                )
                SELECT id FROM thread_messages ORDER BY level, timestamp;
            """, [root.id])
            
            message_ids = [row[0] for row in cursor.fetchall()]
        
        # Return the messages with proper prefetching
        return Message.objects.filter(
            id__in=message_ids
        ).select_related(
            'sender', 'receiver', 'parent_message'
        ).prefetch_related(
            'replies', 'notifications'
        ).order_by('timestamp')

    def get_reply_count(self):
        """Get the total number of replies to this message."""
        return self.replies.count()

    def get_thread_participants(self):
        """Get all users who have participated in this thread."""
        thread_messages = self.get_thread_messages()
        participants = set()
        
        for message in thread_messages:
            participants.add(message.sender)
            participants.add(message.receiver)
            
        return list(participants)


class Notification(models.Model):
    """
    Model to represent notifications sent to users.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="User who will receive this notification"
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Message that triggered this notification"
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the notification was created"
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: New message from {self.message.sender.username}"


class MessageHistory(models.Model):
    """
    Model to store the history of message edits.
    Tracks old content before message updates.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history',
        help_text="Message that was edited"
    )
    old_content = models.TextField(
        help_text="Previous content before the edit"
    )
    edited_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the edit occurred"
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_edits',
        help_text="User who made the edit"
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"Edit history for message {self.message.id} by {self.edited_by.username} at {self.edited_at}"
