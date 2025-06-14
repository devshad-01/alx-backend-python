from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Message, Notification
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
