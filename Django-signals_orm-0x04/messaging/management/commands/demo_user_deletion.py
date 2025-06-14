from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, Notification, MessageHistory


class Command(BaseCommand):
    help = 'Demonstrates user deletion and cleanup signals'

    def handle(self, *args, **options):
        self.stdout.write('=== Django User Deletion Signals Demo ===\n')
        
        # Create test users
        user1, created1 = User.objects.get_or_create(
            username='demo_user_delete',
            defaults={'email': 'delete@demo.com', 'password': 'testpass123'}
        )
        user2, created2 = User.objects.get_or_create(
            username='demo_user_keep',
            defaults={'email': 'keep@demo.com', 'password': 'testpass123'}
        )
        
        if created1:
            user1.set_password('testpass123')
            user1.save()
            self.stdout.write(f'Created user: {user1.username}')
        if created2:
            user2.set_password('testpass123')
            user2.save()
            self.stdout.write(f'Created user: {user2.username}')
        
        # Create test data
        self.stdout.write('\n--- Creating test data ---')
        
        # Messages
        message1 = Message.objects.create(
            sender=user1,
            receiver=user2,
            content='Message from user1 to user2'
        )
        message2 = Message.objects.create(
            sender=user2,
            receiver=user1,
            content='Message from user2 to user1'
        )
        
        # Edit a message to create history
        message1.content = 'Edited message from user1 to user2'
        message1.save()
        
        self.stdout.write(f'Created {Message.objects.count()} messages')
        self.stdout.write(f'Created {Notification.objects.count()} notifications')
        self.stdout.write(f'Created {MessageHistory.objects.count()} edit history records')
        
        # Show data before deletion
        self.stdout.write(f'\n--- Data for {user1.username} before deletion ---')
        self.stdout.write(f'Sent messages: {user1.sent_messages.count()}')
        self.stdout.write(f'Received messages: {user1.received_messages.count()}')
        self.stdout.write(f'Notifications: {user1.notifications.count()}')
        self.stdout.write(f'Message edits: {user1.message_edits.count()}')
        
        # Show total data before deletion
        total_messages_before = Message.objects.count()
        total_notifications_before = Notification.objects.count()
        total_history_before = MessageHistory.objects.count()
        
        self.stdout.write(f'\n--- Total data before deletion ---')
        self.stdout.write(f'Total messages: {total_messages_before}')
        self.stdout.write(f'Total notifications: {total_notifications_before}')
        self.stdout.write(f'Total message history: {total_history_before}')
        
        # Delete user1 (this will trigger the post_delete signal)
        self.stdout.write(f'\n--- Deleting user {user1.username} (triggers signal) ---')
        user1.delete()
        
        # Show data after deletion
        self.stdout.write('\n--- Data after deletion ---')
        self.stdout.write(f'Total messages: {Message.objects.count()}')
        self.stdout.write(f'Total notifications: {Notification.objects.count()}')
        self.stdout.write(f'Total message history: {MessageHistory.objects.count()}')
        
        # Show remaining data for user2
        remaining_user = User.objects.get(username='demo_user_keep')
        self.stdout.write(f'\n--- Remaining data for {remaining_user.username} ---')
        self.stdout.write(f'Sent messages: {remaining_user.sent_messages.count()}')
        self.stdout.write(f'Received messages: {remaining_user.received_messages.count()}')
        self.stdout.write(f'Notifications: {remaining_user.notifications.count()}')
        self.stdout.write(f'Message edits: {remaining_user.message_edits.count()}')
        
        # Calculate cleanup stats
        messages_deleted = total_messages_before - Message.objects.count()
        notifications_deleted = total_notifications_before - Notification.objects.count()
        history_deleted = total_history_before - MessageHistory.objects.count()
        
        self.stdout.write(f'\n--- Cleanup Statistics ---')
        self.stdout.write(f'Messages deleted: {messages_deleted}')
        self.stdout.write(f'Notifications deleted: {notifications_deleted}')
        self.stdout.write(f'History records deleted: {history_deleted}')
        
        self.stdout.write('\n=== User deletion demo completed successfully! ===')
