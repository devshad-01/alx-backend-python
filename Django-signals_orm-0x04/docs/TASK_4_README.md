# Task 4: Custom ORM Manager for Unread Messages

## Overview

This task implements a custom manager in Django's ORM to efficiently filter and retrieve unread messages for users. The implementation enhances the messaging system by providing a streamlined way to check for and display unread messages, improving user experience and application performance.

## Implementation Details

### 1. Added Read Status Field

A boolean field `read` has been added to the `Message` model to track whether a message has been read by the recipient:

```python
class Message(models.Model):
    # ... other fields ...

    read = models.BooleanField(
        default=False,
        help_text="Whether the message has been read by the receiver"
    )

    # ... rest of the model ...
```

By default, messages are marked as unread (`False`) when created. This allows tracking of message status throughout the application.

### 2. Custom Manager Implementation

A dedicated file `managers.py` has been created to house the custom manager implementation:

```python
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
```

The `UnreadMessagesManager` extends Django's base `models.Manager` class with specialized methods:

- `get_queryset()`: Overrides the default method to only return unread messages
- `unread_for_user(user)`: Filters unread messages for a specific receiver
- `unread_messages_count(user)`: Returns the count of unread messages for a user

### 3. Registering the Custom Manager

The custom manager has been added to the `Message` model alongside the default manager:

```python
class Message(models.Model):
    # ... fields ...

    # Custom managers
    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    # ... rest of the model ...
```

This approach preserves the default manager functionality while adding the specialized unread messages manager.

### 4. Optimized Query Implementation

The `list_unread_messages` view function demonstrates the use of the custom manager along with query optimization techniques:

```python
@require_http_methods(["GET"])
def list_unread_messages(request, username=None):
    """
    API endpoint to list only unread messages for a user, with optimized querying.
    Uses the custom UnreadMessagesManager for efficiency.
    """
    try:
        if username:
            user = User.objects.get(username=username)
        else:
            user = request.user

        # Using our custom manager to get only unread messages for this user
        # Optimizing with .only() to fetch only necessary fields
        unread_messages = Message.unread.unread_for_user(user)\
            .select_related('sender')\
            .only('id', 'sender', 'content', 'timestamp', 'parent_message')

        messages_data = []
        for message in unread_messages:
            messages_data.append({
                'id': message.id,
                'sender': message.sender.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'is_reply': message.parent_message is not None
            })

        return JsonResponse({
            'user': username or request.user.username,
            'unread_count': len(messages_data),
            'unread_messages': messages_data
        })

    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

Key optimization techniques used:

1. `Message.unread.unread_for_user(user)`: Uses the custom manager to filter only unread messages
2. `.select_related('sender')`: Reduces database queries by fetching sender data in a single query
3. `.only('id', 'sender', 'content', 'timestamp', 'parent_message')`: Retrieves only necessary fields to minimize data transfer

### 5. Message Read Status Management

Two endpoint functions were implemented to manage message read status:

#### Mark a Single Message as Read

```python
@csrf_exempt
@require_http_methods(["PUT"])
def mark_message_as_read(request, message_id):
    """
    API endpoint to mark a message as read.
    """
    # Implementation details...
    # Includes permission checks and optimized updates
```

#### Mark All Messages as Read

```python
@csrf_exempt
@require_http_methods(["PUT"])
def mark_all_messages_as_read(request):
    """
    API endpoint to mark all unread messages for the current user as read.
    """
    # Implementation details...
    # Includes batch update for efficiency
```

### 6. URL Configuration

URL patterns were added to expose the new functionality:

```python
urlpatterns = [
    # ... existing endpoints ...
    path('unread/<str:username>/', views.list_unread_messages, name='list_unread_messages'),
    path('unread/', views.list_unread_messages, name='list_current_user_unread_messages'),
    path('mark-read/<int:message_id>/', views.mark_message_as_read, name='mark_message_as_read'),
    path('mark-all-read/', views.mark_all_messages_as_read, name='mark_all_messages_as_read'),
]
```

## Benefits

1. **Cleaner API**: The custom manager encapsulates unread message filtering logic, making the code more readable and maintainable.

2. **Performance Optimization**: Using `.only()` and `.select_related()` reduces database load and improves response times.

3. **Enhanced User Experience**: Users can easily see which messages are unread, improving engagement with the messaging system.

4. **Separation of Concerns**: Query logic is isolated in the manager, adhering to Django's "fat models, thin views" philosophy.

5. **Reduced Duplication**: The manager centralizes unread message querying logic, avoiding repetition throughout the codebase.

## Usage Examples

### Getting Unread Messages for a User

```python
# In views
unread_messages = Message.unread.unread_for_user(user)
```

### Counting Unread Messages

```python
# In views or templates
unread_count = Message.unread.unread_messages_count(user)
```

### Marking Messages as Read

```python
# Marking a single message as read
message.read = True
message.save(update_fields=['read'])

# Marking all messages as read for a user
Message.objects.filter(receiver=user, read=False).update(read=True)
```

## Conclusion

The implementation of a custom ORM manager for unread messages demonstrates Django's extensibility and the power of the ORM system. By leveraging these advanced features, we've created a streamlined solution for handling message read status, enhancing both the user experience and the application architecture.
