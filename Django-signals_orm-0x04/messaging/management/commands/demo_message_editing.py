from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from messaging.models import Message, MessageHistory


class Command(BaseCommand):
    help = 'Demonstrates Django signals for message editing and history logging'

    def handle(self, *args, **options):
        self.stdout.write('=== Django Message Editing Signals Demo ===\n')
        
        # Create test users
        user1, created1 = User.objects.get_or_create(
            username='demo_alice',
            defaults={'email': 'alice@demo.com'}
        )
        user2, created2 = User.objects.get_or_create(
            username='demo_bob', 
            defaults={'email': 'bob@demo.com'}
        )
        
        if created1:
            self.stdout.write(f'Created user: {user1.username}')
        if created2:
            self.stdout.write(f'Created user: {user2.username}')
        
        # Create initial message
        self.stdout.write('\n--- Creating initial message ---')
        message = Message.objects.create(
            sender=user1,
            receiver=user2,
            content='Hello Bob! This is the original message content.'
        )
        
        self.stdout.write(f'Created message {message.id}: "{message.content}"')
        self.stdout.write(f'Message edited flag: {message.edited}')
        
        # Edit the message - this will trigger the pre_save signal
        self.stdout.write('\n--- Editing message (triggers pre_save signal) ---')
        message.content = 'Hello Bob! This is the UPDATED message content with new information.'
        message.save()
        
        self.stdout.write(f'Updated message {message.id}: "{message.content}"')
        self.stdout.write(f'Message edited flag: {message.edited}')
        
        # Check message history
        history_records = MessageHistory.objects.filter(message=message)
        self.stdout.write(f'\nMessage edit history records: {history_records.count()}')
        
        for i, record in enumerate(history_records, 1):
            self.stdout.write(f'History {i}:')
            self.stdout.write(f'  - Old content: "{record.old_content}"')
            self.stdout.write(f'  - Edited by: {record.edited_by.username}')
            self.stdout.write(f'  - Edited at: {record.edited_at}')
        
        # Edit again to show multiple history records
        self.stdout.write('\n--- Editing message again ---')
        message.content = 'Hello Bob! This is the FINAL version of the message after multiple edits.'
        message.save()
        
        # Check updated history
        history_records = MessageHistory.objects.filter(message=message)
        self.stdout.write(f'\nFinal message edit history records: {history_records.count()}')
        
        for i, record in enumerate(history_records, 1):
            self.stdout.write(f'History {i}:')
            self.stdout.write(f'  - Old content: "{record.old_content[:50]}..."')
            self.stdout.write(f'  - Edited by: {record.edited_by.username}')
            self.stdout.write(f'  - Edited at: {record.edited_at}')
        
        self.stdout.write(f'\nCurrent message content: "{message.content}"')
        self.stdout.write(f'Message edited flag: {message.edited}')
        
        self.stdout.write('\n=== Message editing demo completed successfully! ===')
