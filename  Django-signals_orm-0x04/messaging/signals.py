from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, Notification, MessageHistory


@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """
    Signal handler that creates a notification when a new message is created.
    
    Args:
        sender: The model class (Message)
        instance: The actual instance being saved (Message instance)
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        # Create notification for the receiver of the message
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )
        print(f"Notification created for user {instance.receiver.username} about message from {instance.sender.username}")


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler that logs the old content of a message before it's updated.
    
    Args:
        sender: The model class (Message)
        instance: The actual instance being saved (Message instance)
        **kwargs: Additional keyword arguments
    """
    # Only process if this is an update (not a new message)
    if instance.pk:
        try:
            # Get the old version of the message from database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has actually changed
            if old_message.content != instance.content:
                # Create a history record with the old content
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_message.content,
                    edited_by=instance.sender,  # Assuming sender is editing their own message
                    edited_at=timezone.now()
                )
                
                # Mark the message as edited
                instance.edited = True
                instance.edited_at = timezone.now()
                
                print(f"Message edit logged: User {instance.sender.username} edited message {instance.pk}")
                
        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass
