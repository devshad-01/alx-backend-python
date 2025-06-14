from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, Notification


class Command(BaseCommand):
    help = 'Demonstrate the Django signals functionality for message notifications'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Django Signals Demo ==='))
        
        # Create test users
        sender, created = User.objects.get_or_create(
            username='alice',
            defaults={
                'email': 'alice@example.com',
                'first_name': 'Alice',
                'last_name': 'Smith'
            }
        )
        if created:
            sender.set_password('testpass123')
            sender.save()
            self.stdout.write(f'Created sender user: {sender.username}')
        
        receiver, created = User.objects.get_or_create(
            username='bob',
            defaults={
                'email': 'bob@example.com',
                'first_name': 'Bob',
                'last_name': 'Johnson'
            }
        )
        if created:
            receiver.set_password('testpass123')
            receiver.save()
            self.stdout.write(f'Created receiver user: {receiver.username}')
        
        # Show initial notification count
        initial_count = Notification.objects.filter(user=receiver).count()
        self.stdout.write(f'Initial notifications for {receiver.username}: {initial_count}')
        
        # Create a message (this should trigger the signal)
        self.stdout.write('\n--- Creating a new message ---')
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content="Hello Bob! This is an automated message to test Django signals."
        )
        
        # Check if notification was created
        final_count = Notification.objects.filter(user=receiver).count()
        self.stdout.write(f'Final notifications for {receiver.username}: {final_count}')
        
        if final_count > initial_count:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ SUCCESS: Signal worked! Notification automatically created for {receiver.username}'
                )
            )
            
            # Show the notification details
            notification = Notification.objects.filter(user=receiver).latest('created_at')
            self.stdout.write(f'Notification ID: {notification.id}')
            self.stdout.write(f'Notification for: {notification.user.username}')
            self.stdout.write(f'Message from: {notification.message.sender.username}')
            self.stdout.write(f'Message content: {notification.message.content[:50]}...')
            self.stdout.write(f'Is read: {notification.is_read}')
            self.stdout.write(f'Created at: {notification.created_at}')
        else:
            self.stdout.write(
                self.style.ERROR('❌ FAILED: Signal did not work - no notification created')
            )
        
        self.stdout.write('\n=== Demo Complete ===')
