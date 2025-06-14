# Django Signals and ORM - Task 0: Message Notifications

This project implements Django signals to automatically notify users when they receive new messages.

## Project Structure

```
Django-signals_orm-0x04/
├── manage.py
├── messaging/
│   ├── models.py          # Contains Message and Notification models
│   ├── signals.py         # Contains signal handlers for notifications
│   ├── apps.py            # App configuration with signal loading
│   ├── admin.py           # Admin interface for models
│   ├── tests.py           # Tests for signal functionality
│   ├── views.py           # API views for messaging
│   ├── urls.py            # URL routing for messaging app
│   └── management/
│       └── commands/
│           └── demo_signals.py  # Demo command
└── messaging_project/
    ├── settings.py        # Django settings
    └── urls.py            # Main URL configuration
```

## Features Implemented

### 1. Models
- **Message**: Represents messages sent between users with sender, receiver, content, and timestamp
- **Notification**: Represents notifications linked to users and messages

### 2. Django Signals
- Automatic notification creation when a new message is saved
- Uses `post_save` signal on the Message model
- Signal handler in `messaging/signals.py`
- Properly configured in `apps.py` to load signals

### 3. Admin Interface
- Custom admin for both Message and Notification models
- Easy management and viewing of data through Django admin

### 4. Tests
- Comprehensive test suite to verify signal functionality
- Tests for notification creation, multiple messages, and update scenarios

### 5. API Endpoints
- `POST /messaging/send/` - Send a message and trigger notification
- `GET /messaging/notifications/<username>/` - List notifications for a user

## How It Works

1. When a new `Message` instance is created and saved to the database
2. The `post_save` signal is triggered
3. The signal handler `create_notification_on_message` automatically creates a `Notification` instance
4. The notification is linked to the receiver of the message

## Setup and Usage

1. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

3. **Run tests:**
   ```bash
   python manage.py test messaging
   ```

4. **Demo the signals:**
   ```bash
   python manage.py demo_signals
   ```

5. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

## API Usage Examples

### Send a Message (triggers notification)
```bash
curl -X POST http://localhost:8000/messaging/send/ \
  -H "Content-Type: application/json" \
  -d '{
    "sender_username": "alice", 
    "receiver_username": "bob", 
    "content": "Hello Bob!"
  }'
```

### List Notifications
```bash
curl http://localhost:8000/messaging/notifications/bob/
```

## Signal Implementation Details

The signal is implemented in `messaging/signals.py`:

```python
@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )
```

This ensures that every time a new message is created, a notification is automatically generated for the receiving user, demonstrating the power of Django's signal system for decoupled, event-driven architecture.

## Best Practices Implemented

1. **Signal Registration**: Signals are properly registered in `apps.py` using the `ready()` method
2. **Test Coverage**: Comprehensive tests verify signal functionality
3. **Decoupling**: Business logic (notification creation) is decoupled from the model save logic
4. **Admin Interface**: Proper admin configuration for easy data management
5. **Documentation**: Clear documentation and examples
