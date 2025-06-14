from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch, Q
from .models import Message, Notification, MessageHistory
import json


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """
    API endpoint to send a message and demonstrate signal functionality.
    This will automatically create a notification via Django signals.
    """
    try:
        data = json.loads(request.body)
        receiver_username = data.get('receiver_username')
        content = data.get('content')
        parent_id = data.get('parent_id')  # For threaded replies
        
        if not all([receiver_username, content]):
            return JsonResponse({
                'error': 'receiver_username and content are required'
            }, status=400)
        
        try:
            # Using request.user instead of getting from data
            sender = request.user
            receiver = User.objects.get(username=receiver_username)
            
            # Handle parent message for threaded replies
            parent_message = None
            if parent_id:
                try:
                    parent_message = Message.objects.get(id=parent_id)
                except Message.DoesNotExist:
                    return JsonResponse({'error': 'Parent message not found'}, status=404)
            
        except User.DoesNotExist as e:
            return JsonResponse({'error': f'User not found: {str(e)}'}, status=404)
        
        # Create the message - this will trigger the signal
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            parent_message=parent_message
        )
        
        # Check if notification was created - using select_related for optimization
        notification = Notification.objects.filter(
            user=receiver,
            message=message
        ).select_related('message', 'user').first()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': sender.username,
                'receiver': receiver.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'parent_id': parent_message.id if parent_message else None
            },
            'notification_created': notification is not None,
            'notification': {
                'id': notification.id if notification else None,
                'is_read': notification.is_read if notification else None,
                'created_at': notification.created_at.isoformat() if notification else None
            } if notification else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def list_notifications(request, username):
    """
    API endpoint to list notifications for a user.
    """
    try:
        user = User.objects.get(username=username)
        
        # Using select_related to optimize database queries
        notifications = Notification.objects.filter(user=user)\
            .select_related('message', 'message__sender', 'user')\
            .order_by('-created_at')
        
        notifications_data = []
        for notification in notifications:
            notifications_data.append({
                'id': notification.id,
                'message': {
                    'sender': notification.message.sender.username,
                    'content': notification.message.content,
                    'timestamp': notification.message.timestamp.isoformat()
                },
                'is_read': notification.is_read,
                'created_at': notification.created_at.isoformat()
            })
        
        return JsonResponse({
            'user': username,
            'notifications_count': len(notifications_data),
            'notifications': notifications_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def edit_message(request, message_id):
    """
    API endpoint to edit a message.
    This will trigger the pre_save signal to log the edit history.
    """
    try:
        data = json.loads(request.body)
        new_content = data.get('content')
        
        if not new_content:
            return JsonResponse({
                'error': 'content is required'
            }, status=400)
        
        try:
            # Using select_related for optimization
            message = Message.objects.select_related('sender', 'receiver').get(id=message_id)
            
            # Using request.user instead of getting from data
            editor = request.user
            
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        
        # Check if editor is the sender (basic permission check)
        if message.sender != editor:
            return JsonResponse({
                'error': 'Only the message sender can edit the message'
            }, status=403)
        
        # Store old content for response
        old_content = message.content
        
        # Update message content - this will trigger the pre_save signal
        message.content = new_content
        message.save()
        
        # Get the history record that was just created
        history = MessageHistory.objects.filter(message=message).select_related('message', 'edited_by').first()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'old_content': old_content,
                'new_content': new_content,
                'edited': message.edited,
                'edit_logged': history is not None
            }
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def message_history(request, message_id):
    """
    API endpoint to view the edit history of a message.
    """
    try:
        # Using select_related for optimization
        message = Message.objects.select_related('sender', 'receiver').get(id=message_id)
        
        # Using select_related to optimize database queries
        history_records = MessageHistory.objects.filter(message=message)\
            .select_related('message', 'edited_by')
        
        history_data = []
        for record in history_records:
            history_data.append({
                'id': record.id,
                'old_content': record.old_content,
                'edited_at': record.edited_at.isoformat(),
                'edited_by': record.edited_by.username
            })
        
        return JsonResponse({
            'message_id': message.id,
            'current_content': message.content,
            'edited': message.edited,
            'history': history_data,
            'history_count': len(history_data)
        })
        
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])  
def user_message_edits(request, username):
    """
    API endpoint to view all message edits made by a specific user.
    """
    try:
        user = User.objects.get(username=username)
        
        # Using select_related to optimize database queries
        edits = MessageHistory.objects.filter(edited_by=user)\
            .select_related('message', 'message__receiver', 'edited_by')
        
        edits_data = []
        for edit in edits:
            edits_data.append({
                'id': edit.id,
                'message_id': edit.message.id,
                'old_content': edit.old_content,
                'current_content': edit.message.content,
                'edited_at': edit.edited_at.isoformat(),
                'message_receiver': edit.message.receiver.username
            })
        
        return JsonResponse({
            'user': username,
            'edits': edits_data,
            'total_edits': len(edits_data)
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE", "POST"])
def delete_user(request, username):
    """
    API endpoint that allows a user to delete their account.
    This will trigger the post_delete signal to clean up related data.
    
    Args:
        request: HTTP request object
        username: Username of the user to delete
    
    Returns:
        JsonResponse with deletion status
    """
    try:
        # Get the user to delete
        user = User.objects.get(username=username)
        
        # Store user info for response before deletion
        user_id = user.id
        user_info = {
            'id': user_id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None
        }
        
        # Count related data before deletion
        related_data_count = {
            'sent_messages': user.sent_messages.count(),
            'received_messages': user.received_messages.count(),
            'notifications': user.notifications.count(),
            'message_edits': user.message_edits.count()
        }
        
        print(f"Deleting user: {user.username} (ID: {user_id})")
        print(f"Related data to be cleaned up: {related_data_count}")
        
        # Delete the user - this will trigger the post_delete signal
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User account {username} has been successfully deleted',
            'deleted_user': user_info,
            'cleaned_up_data': related_data_count,
            'note': 'All related messages, notifications, and history have been automatically cleaned up via Django signals'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'error': f'User with username "{username}" not found'
        }, status=404)
    
    except Exception as e:
        return JsonResponse({
            'error': f'Failed to delete user: {str(e)}'
        }, status=500)


def get_user_data_summary(request, username):
    """
    API endpoint to get a summary of user's data before deletion.
    Helps users understand what will be deleted.
    """
    try:
        user = User.objects.get(username=username)
        
        # Get counts of related data
        sent_messages = user.sent_messages.count()
        received_messages = user.received_messages.count()
        notifications = user.notifications.count()
        message_edits = user.message_edits.count()
        
        return JsonResponse({
            'username': username,
            'data_summary': {
                'sent_messages': sent_messages,
                'received_messages': received_messages,
                'notifications': notifications,
                'message_edit_history': message_edits,
                'total_items': sent_messages + received_messages + notifications + message_edits
            },
            'warning': 'All this data will be permanently deleted if you delete your account'
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_threaded_message(request, message_id):
    """
    API endpoint to get a message with all of its replies in a threaded format.
    Uses recursive querying to fetch the entire tree of replies.
    """
    try:
        # Get the root message with all necessary relations for optimization
        root_message = Message.objects.filter(id=message_id)\
            .select_related('sender', 'receiver')\
            .first()
        
        if not root_message:
            return JsonResponse({'error': 'Message not found'}, status=404)
            
        # Get the message thread recursively
        message_thread = get_message_with_replies(root_message)
        
        return JsonResponse({
            'message_thread': message_thread
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_message_with_replies(message):
    """
    Helper function to recursively fetch all replies to a message.
    Used by get_threaded_message to build a threaded conversation view.
    """
    # Optimize query using select_related to reduce db hits
    replies = Message.objects.filter(parent_message=message)\
        .select_related('sender', 'receiver')\
        .prefetch_related(
            Prefetch('notification_set', queryset=Notification.objects.select_related('user'))
        )
        
    message_data = {
        'id': message.id,
        'sender': message.sender.username,
        'receiver': message.receiver.username,
        'content': message.content,
        'timestamp': message.timestamp.isoformat(),
        'edited': message.edited,
        'replies': []
    }
    
    # Recursively get replies to each reply
    for reply in replies:
        reply_data = get_message_with_replies(reply)
        message_data['replies'].append(reply_data)
        
    return message_data


@require_http_methods(["GET"])
def list_messages(request, username=None):
    """
    API endpoint to list messages for a user, with optimized querying.
    """
    try:
        query_params = {}
        
        if username:
            # Get all messages sent or received by this user
            user = User.objects.get(username=username)
            query = Q(sender=user) | Q(receiver=user)
        else:
            # Only get messages related to the requesting user if no username provided
            user = request.user
            query = Q(sender=user) | Q(receiver=user)
        
        # Using both select_related and prefetch_related for optimization
        messages = Message.objects.filter(query, parent_message=None)\
            .select_related('sender', 'receiver')\
            .prefetch_related(
                # Prefetch direct replies with their related fields
                Prefetch('replies', 
                         queryset=Message.objects.select_related('sender', 'receiver')),
                # Prefetch notifications related to messages
                Prefetch('notification_set', 
                         queryset=Notification.objects.select_related('user'))
            ).order_by('-timestamp')
        
        messages_data = []
        for message in messages:
            # Get reply counts
            reply_count = message.replies.count()
            
            messages_data.append({
                'id': message.id,
                'sender': message.sender.username,
                'receiver': message.receiver.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'edited': message.edited,
                'reply_count': reply_count,
                'has_replies': reply_count > 0
            })
        
        return JsonResponse({
            'user': username or request.user.username,
            'messages_count': len(messages_data),
            'messages': messages_data
        })
        
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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


@csrf_exempt
@require_http_methods(["PUT"])
def mark_message_as_read(request, message_id):
    """
    API endpoint to mark a message as read.
    """
    try:
        # Using select_related for optimization
        message = Message.objects.select_related('sender', 'receiver').get(id=message_id)
        
        # Only the receiver can mark a message as read
        if message.receiver != request.user:
            return JsonResponse({
                'error': 'Only the message receiver can mark the message as read'
            }, status=403)
        
        # Update read status
        if not message.read:
            message.read = True
            message.save(update_fields=['read'])
            status_changed = True
        else:
            status_changed = False
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'read': message.read,
            'status_changed': status_changed
        })
        
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["PUT"])
def mark_all_messages_as_read(request):
    """
    API endpoint to mark all unread messages for the current user as read.
    """
    try:
        # Get count before update
        unread_count = Message.unread.unread_for_user(request.user).count()
        
        # Update all unread messages for this user
        updated = Message.objects.filter(receiver=request.user, read=False).update(read=True)
        
        return JsonResponse({
            'success': True,
            'messages_marked_as_read': updated,
            'previous_unread_count': unread_count,
            'current_unread_count': 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
