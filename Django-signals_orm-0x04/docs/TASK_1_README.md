# Django Signals and ORM - Task 1: Message Edit Logging

This task implements Django signals to automatically log message edits and track edit history.

## Features Implemented

### 1. Enhanced Message Model

- Added `edited` boolean field to track if a message has been modified
- Automatically set to `True` when content changes

### 2. MessageHistory Model

- Stores old content before edits
- Tracks who made the edit and when
- Links to the original message

### 3. Pre-Save Signal

- Logs message edits before they're saved to database
- Creates MessageHistory record with old content
- Only triggers on content changes, not new messages

### 4. Admin Interface

- Enhanced Message admin to show edit status
- Read-only MessageHistory admin for viewing edit logs
- Preview of old content in history records

### 5. API Endpoints

- `PUT /messaging/edit/<message_id>/` - Edit a message
- `GET /messaging/history/<message_id>/` - View message edit history

## How It Works

1. When a message's content is modified and saved
2. The `pre_save` signal captures the old content
3. A MessageHistory record is created automatically
4. The message's `edited` field is set to `True`
5. Users can view complete edit history through admin or API

## Testing

Run the demo command to see message editing in action:

```bash
python manage.py demo_message_editing
```

Run tests:

```bash
python manage.py test messaging.MessageEditTestCase
```

## API Usage

### Edit a Message

```bash
curl -X PUT http://localhost:8000/messaging/edit/1/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Updated message content"}'
```

### View Edit History

```bash
curl http://localhost:8000/messaging/history/1/
```

This implementation demonstrates Django's signal system for automated logging and audit trails.
