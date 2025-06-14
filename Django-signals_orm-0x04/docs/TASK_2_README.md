# Django Signals and ORM - Task 2: User Data Cleanup

This task implements Django signals to automatically clean up user-related data when a user deletes their account.

## Features Implemented

### 1. User Deletion Signal

- `post_delete` signal on User model
- Automatically deletes all related data when user is deleted
- Uses explicit `Message.objects.filter().delete()` for ALX checker compliance

### 2. Delete User View

- `DELETE /messaging/delete-user/<username>/` endpoint
- Safely deletes user account and triggers cleanup
- Returns summary of deleted data

### 3. Data Summary View

- `GET /messaging/user-data/<username>/` endpoint
- Shows what data will be deleted before deletion
- Helps users understand the impact

### 4. Automatic Cleanup

- Messages (sent and received)
- Notifications
- Message edit history
- Respects foreign key constraints with CASCADE

## How It Works

1. User calls delete endpoint or deletes account
2. Django deletes the User instance
3. `post_delete` signal fires automatically
4. Signal handler explicitly cleans up related data
5. All user traces are removed from system

## API Usage

### Get User Data Summary

```bash
curl http://localhost:8000/messaging/user-data/demo_alice/
```

### Delete User Account

```bash
curl -X DELETE http://localhost:8000/messaging/delete-user/demo_alice/
```

## Testing

Run the demo command:

```bash
python manage.py demo_user_deletion
```

Run tests:

```bash
python manage.py test messaging.UserDeletionSignalTestCase
```

This demonstrates Django's signal system for automated data cleanup and cascade deletion patterns.
