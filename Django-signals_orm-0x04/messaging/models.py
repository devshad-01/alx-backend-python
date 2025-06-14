from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Message(models.Model):
    """
    Model to represent a message sent between users.
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

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}: {self.content[:50]}{'...' if len(self.content) > 50 else ''}"


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
