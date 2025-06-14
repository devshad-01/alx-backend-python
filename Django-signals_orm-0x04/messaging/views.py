from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
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
        sender_username = data.get('sender_username')
        receiver_username = data.get('receiver_username')
        content = data.get('content')
        
        if not all([sender_username, receiver_username, content]):
            return JsonResponse({
                'error': 'sender_username, receiver_username, and content are required'
            }, status=400)
        
        try:
            sender = User.objects.get(username=sender_username)
            receiver = User.objects.get(username=receiver_username)
        except User.DoesNotExist as e:
            return JsonResponse({'error': f'User not found: {str(e)}'}, status=404)
        
        # Create the message - this will trigger the signal
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        
        # Check if notification was created
        notification = Notification.objects.filter(
            user=receiver,
            message=message
        ).first()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': sender.username,
                'receiver': receiver.username,
                'content': message.content,
                'timestamp': message.timestamp.isoformat()
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
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        
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
        editor_username = data.get('editor_username')
        
        if not all([new_content, editor_username]):
            return JsonResponse({
                'error': 'content and editor_username are required'
            }, status=400)
        
        try:
            message = Message.objects.get(id=message_id)
            editor = User.objects.get(username=editor_username)
        except Message.DoesNotExist:
            return JsonResponse({'error': 'Message not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Editor user not found'}, status=404)
        
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
        history = MessageHistory.objects.filter(message=message).first()
        
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
        message = Message.objects.get(id=message_id)
        history_records = MessageHistory.objects.filter(message=message)
        
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
        edits = MessageHistory.objects.filter(edited_by=user)
        
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
