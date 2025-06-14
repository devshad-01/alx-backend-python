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
    
    def test_message_edit_within_signal_triggers_no_additional_notifications(self):
        """Test that editing a message within the signal does not create additional notifications"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial content"
        )
        
        # Edit the message within the signal (simulating complex signal behavior)
        message.content = "Edited within signal"
        message.save()
        
        # There should still be only 1 notification (for the initial message creation)
        self.assertEqual(Notification.objects.count(), 1)
        
        # Check the notification details
        notification = Notification.objects.first()
        self.assertEqual(notification.message, message)
    
    def test_message_edit_creates_history_only_once_per_edit(self):
        """Test that editing a message creates a history record only once per edit action"""
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial content"
        )
        
        # Edit the message
        message.content = "First edit"
        message.save()
        
        # Edit the message again (simulating quick successive edits)
        message.content = "Second edit"
        message.save()
        
        # Check that only two history records were created (one for each edit)
        self.assertEqual(MessageHistory.objects.count(), 2)
        
        # Check the content of the last history record
        last_history = MessageHistory.objects.last()
        self.assertEqual(last_history.old_content, "First edit")


class UserDeletionSignalTestCase(TestCase):
    """Test cases for user deletion and cleanup signals"""
    
    def setUp(self):
        """Set up test data"""
        self.user1 = User.objects.create_user(
            username='user_to_delete',
            email='delete@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='other_user',
            email='other@example.com',
            password='testpass123'
        )
        
        # Create some test data for user1
        self.message1 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Message from user1 to user2"
        )
        self.message2 = Message.objects.create(
            sender=self.user2,
            receiver=self.user1,
            content="Message from user2 to user1"
        )
        
        # Edit a message to create history
        self.message1.content = "Edited message content"
        self.message1.save()
    
    def test_user_deletion_cleans_up_related_data(self):
        """Test that deleting a user cleans up all related data"""
        # Verify initial data exists
        self.assertEqual(Message.objects.count(), 2)
        self.assertEqual(Notification.objects.count(), 2)  # One for each message
        self.assertEqual(MessageHistory.objects.count(), 1)  # From the edit
        
        # Get counts specific to user1
        user1_sent_messages = self.user1.sent_messages.count()
        user1_received_messages = self.user1.received_messages.count()
        user1_notifications = self.user1.notifications.count()
        user1_message_edits = self.user1.message_edits.count()
        
        self.assertEqual(user1_sent_messages, 1)
        self.assertEqual(user1_received_messages, 1)
        self.assertEqual(user1_notifications, 1)
        self.assertEqual(user1_message_edits, 1)
        
        # Delete user1 (this should trigger the post_delete signal)
        self.user1.delete()
        
        # Verify user1's data is gone
        # Messages sent by user1 should be deleted (CASCADE)
        self.assertEqual(Message.objects.filter(sender__username='user_to_delete').count(), 0)
        
        # Messages received by user1 should be deleted (CASCADE)
        self.assertEqual(Message.objects.filter(receiver__username='user_to_delete').count(), 0)
        
        # Notifications for user1 should be deleted (CASCADE)
        self.assertEqual(Notification.objects.filter(user__username='user_to_delete').count(), 0)
        
        # Message history by user1 should be deleted (CASCADE)
        self.assertEqual(MessageHistory.objects.filter(edited_by__username='user_to_delete').count(), 0)
        
        # Verify that user2's data is unaffected
        self.assertTrue(User.objects.filter(username='other_user').exists())
    
    def test_cascade_deletion_behavior(self):
        """Test that CASCADE foreign keys work correctly"""
        # Create additional test data
        message3 = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Another message"
        )
        
        # Count total data before deletion
        total_messages_before = Message.objects.count()
        total_notifications_before = Notification.objects.count()
        total_history_before = MessageHistory.objects.count()
        
        # Delete user1
        self.user1.delete()
        
        # Verify CASCADE deletions occurred
        # All messages involving user1 should be deleted
        self.assertLess(Message.objects.count(), total_messages_before)
        self.assertLess(Notification.objects.count(), total_notifications_before)
        self.assertLess(MessageHistory.objects.count(), total_history_before)
        
        # User2 should still exist
        self.assertTrue(User.objects.filter(username='other_user').exists())
    
    def test_user_deletion_signal_logging(self):
        """Test that the post_delete signal logs properly"""
        # This test verifies that the signal is called
        # In a real scenario, you might capture the print statements
        # or use logging and test log outputs
        
        # Count data before deletion
        sent_count = self.user1.sent_messages.count()
        received_count = self.user1.received_messages.count()
        notifications_count = self.user1.notifications.count()
        edits_count = self.user1.message_edits.count()
        
        # Verify we have data to delete
        self.assertGreater(sent_count, 0)
        self.assertGreater(received_count, 0)
        self.assertGreater(notifications_count, 0)
        self.assertGreater(edits_count, 0)
        
        # Delete user (signal should fire)
        username = self.user1.username
        self.user1.delete()
        
        # Verify user is deleted
        self.assertFalse(User.objects.filter(username=username).exists())
