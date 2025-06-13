from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom admin for User model"""
    list_display = ['user_id', 'username', 'email', 'first_name', 'last_name', 'is_online', 'created_at']
    list_filter = ['is_online', 'is_staff', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'is_online')
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin for Conversation model"""
    list_display = ['conversation_id', 'get_participants', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    filter_horizontal = ['participants']
    
    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin for Message model"""
    list_display = ['message_id', 'sender', 'conversation', 'content_preview', 'timestamp', 'is_read']
    list_filter = ['timestamp', 'is_read']
    search_fields = ['message_body', 'sender__username']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.message_body[:50] + '...' if len(obj.message_body) > 50 else obj.message_body
    content_preview.short_description = 'Content Preview'
