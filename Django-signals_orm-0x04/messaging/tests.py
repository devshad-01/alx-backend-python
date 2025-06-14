from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification


class MessageSignalTestCase(TestCase):
    """Test case for message signals functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.sender = User.objects.create_user(
            username='sender_user',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver_user',
            email='receiver@example.com',
            password='testpass123'
        )
    
    def test_notification_created_on_message_save(self):
        """Test that a notification is automatically created when a message is saved"""
        # Initially no notifications should exist
        self.assertEqual(Notification.objects.count(), 0)
        
        # Create a new message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello! This is a test message."
        )
        
        # Check that a notification was automatically created
        self.assertEqual(Notification.objects.count(), 1)
        
        # Check the notification details
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_multiple_messages_create_multiple_notifications(self):
        """Test that multiple messages create multiple notifications"""
        # Create multiple messages
        for i in range(3):
            Message.objects.create(
                sender=self.sender,
                receiver=self.receiver,
                content=f"Test message {i + 1}"
            )
        
        # Should have 3 notifications
        self.assertEqual(Notification.objects.count(), 3)
        
        # All notifications should be for the receiver
        notifications = Notification.objects.all()
        for notification in notifications:
            self.assertEqual(notification.user, self.receiver)
            self.assertFalse(notification.is_read)
    
    def test_no_notification_on_message_update(self):
        """Test that updating a message doesn't create additional notifications"""
        # Create initial message
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )
        
        # Should have 1 notification
        self.assertEqual(Notification.objects.count(), 1)
        
        # Update the message
        message.content = "Updated content"
        message.save()
        
        # Should still have only 1 notification
        self.assertEqual(Notification.objects.count(), 1)
    
    def test_notification_links_to_correct_message(self):
        """Test that notification is properly linked to the correct message"""
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Link test message"
        )
        
        notification = Notification.objects.first()
        self.assertEqual(notification.message.id, message.id)
        self.assertEqual(notification.message.sender, self.sender)
        self.assertEqual(notification.message.receiver, self.receiver)
        self.assertEqual(notification.message.content, "Link test message")
