from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory


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


class MessageEditTestCase(TestCase):
    """Test cases for message editing functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='testpass123'
        )
    
    def test_message_edit_creates_history(self):
        """Test that editing a message creates a history record"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message content"
        )
        
        # Initially no history should exist
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(message.edited)
        
        # Edit the message
        message.content = "Updated message content"
        message.save()
        
        # Check that history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        
        # Check history details
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, message)
        self.assertEqual(history.old_content, "Original message content")
        self.assertEqual(history.edited_by, self.user1)
        self.assertIsNotNone(history.edited_at)
        
        # Check that message is marked as edited
        message.refresh_from_db()
        self.assertTrue(message.edited)
    
    def test_multiple_edits_create_multiple_history_records(self):
        """Test that multiple edits create multiple history records"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # First edit
        message.content = "First edit"
        message.save()
        
        # Second edit
        message.content = "Second edit"
        message.save()
        
        # Third edit
        message.content = "Third edit"
        message.save()
        
        # Check that three history records were created
        self.assertEqual(MessageHistory.objects.count(), 3)
        
        # Check the history records are in correct order
        history_records = MessageHistory.objects.filter(message=message).order_by('edited_at')
        self.assertEqual(history_records[0].old_content, "Original content")
        self.assertEqual(history_records[1].old_content, "First edit")
        self.assertEqual(history_records[2].old_content, "Second edit")
        
        # Check final message content
        message.refresh_from_db()
        self.assertEqual(message.content, "Third edit")
        self.assertTrue(message.edited)
    
    def test_no_history_created_when_content_unchanged(self):
        """Test that no history is created when content doesn't change"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Unchanged content"
        )
        
        # Save without changing content
        message.save()
        
        # No history should be created
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(message.edited)
    
    def test_history_tracks_correct_editor(self):
        """Test that history correctly tracks who made the edit"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original content"
        )
        
        # Edit the message
        message.content = "Edited content"
        message.save()
        
        # Check that history records the correct editor
        history = MessageHistory.objects.first()
        self.assertEqual(history.edited_by, self.user1)
    
    def test_notification_still_created_on_message_creation(self):
        """Test that notifications are still created when messages are created (not affected by edit signals)"""
        # Create a message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="New message"
        )
        
        # Check notification was created
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
