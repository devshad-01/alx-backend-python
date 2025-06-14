"""
Custom model managers for the messaging app.
"""
from django.db import models
from django.db.models import Q


class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    """
    def get_queryset(self):
        """Return only unread messages."""
        return super().get_queryset().filter(read=False)
    
    def unread_for_user(self, user):
        """
        Return unread messages where the user is the receiver.
        
        Args:
            user: The User object
            
        Returns:
            QuerySet of unread messages for the user
        """
        return self.get_queryset().filter(receiver=user)
    
    def unread_messages_count(self, user):
        """
        Return the count of unread messages for a user.
        
        Args:
            user: The User object
            
        Returns:
            Integer count of unread messages
        """
        return self.unread_for_user(user).count()
