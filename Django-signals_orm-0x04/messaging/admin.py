from django.contrib import admin
from .models import Message, Notification, MessageHistory


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    list_display = ['id', 'sender', 'receiver', 'content_preview', 'edited', 'timestamp']
    list_filter = ['timestamp', 'edited', 'sender', 'receiver']
    search_fields = ['content', 'sender__username', 'receiver__username']
    readonly_fields = ['timestamp', 'edited']
    
    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    list_display = ['id', 'user', 'message_sender', 'message_preview', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'user']
    search_fields = ['user__username', 'message__content', 'message__sender__username']
    readonly_fields = ['created_at', 'message']
    
    def message_sender(self, obj):
        """Display the sender of the related message"""
        return obj.message.sender.username
    message_sender.short_description = 'Message Sender'
    
    def message_preview(self, obj):
        """Show preview of the related message content"""
        content = obj.message.content
        return content[:30] + '...' if len(content) > 30 else content
    message_preview.short_description = 'Message Preview'


@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    """Admin interface for MessageHistory model"""
    list_display = ['id', 'message', 'edited_by', 'old_content_preview', 'edited_at']
    list_filter = ['edited_at', 'edited_by']
    search_fields = ['old_content', 'message__content', 'edited_by__username']
    readonly_fields = ['message', 'old_content', 'edited_at', 'edited_by']
    
    def old_content_preview(self, obj):
        """Show preview of old message content"""
        return obj.old_content[:50] + '...' if len(obj.old_content) > 50 else obj.old_content
    old_content_preview.short_description = 'Old Content Preview'
    
    def has_add_permission(self, request):
        """Disable adding new history records through admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing history records through admin"""
        return False
