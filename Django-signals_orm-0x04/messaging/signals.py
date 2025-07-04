from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification


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
    Signal handler that logs message edits before the message is updated.
    
    Args:
        sender: The model class (Message)
        instance: The actual instance being saved (Message instance)
        **kwargs: Additional keyword arguments
    """
    # Import here to avoid circular imports
    from .models import MessageHistory
    
    # Check if this is an update (not a new message)
    if instance.pk:
        try:
            # Get the existing message from database
            old_message = Message.objects.get(pk=instance.pk)
            
            # Check if content has changed
            if old_message.content != instance.content:
                # Create history record
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=instance.sender  # Assuming sender is doing the edit
                )
                
                # Mark message as edited
                instance.edited = True
                
                print(f"Message edit logged: Message {instance.pk} content changed from '{old_message.content[:50]}...' to '{instance.content[:50]}...'")
                
        except Message.DoesNotExist:
            # This shouldn't happen, but handle gracefully
            pass


@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Signal handler that cleans up user-related data when a user is deleted.
    
    Args:
        sender: The model class (User)
        instance: The actual instance being deleted (User instance)
        **kwargs: Additional keyword arguments
    """
    from .models import MessageHistory
    
    username = instance.username
    user_id = instance.id
    
    print(f"User deletion cleanup for '{username}' (ID: {user_id}):")
    
    # Clean up messages sent by this user
    sent_messages = Message.objects.filter(sender=instance)
    sent_count = sent_messages.count()
    print(f"  - Deleting {sent_count} sent messages")
    sent_messages.delete()
    
    # Clean up messages received by this user
    received_messages = Message.objects.filter(receiver=instance)
    received_count = received_messages.count()
    print(f"  - Deleting {received_count} received messages")
    received_messages.delete()
    
    # Clean up notifications for this user
    user_notifications = Notification.objects.filter(user=instance)
    notifications_count = user_notifications.count()
    print(f"  - Deleting {notifications_count} notifications")
    user_notifications.delete()
    
    # Clean up message edit history by this user
    user_message_edits = MessageHistory.objects.filter(edited_by=instance)
    edits_count = user_message_edits.count()
    print(f"  - Deleting {edits_count} message edit history records")
    user_message_edits.delete()
    
    print(f"User '{username}' and all related data have been cleaned up successfully")
