from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('notifications/<str:username>/', views.list_notifications, name='list_notifications'),
    path('edit/<int:message_id>/', views.edit_message, name='edit_message'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
    path('user-edits/<str:username>/', views.user_message_edits, name='user_message_edits'),
    path('delete-user/', views.delete_user, name='delete_user'),
    path('user-summary/<str:username>/', views.get_user_data_summary, name='user_data_summary'),
    path('messages/<str:username>/', views.list_messages, name='list_messages'),
    path('messages/', views.list_messages, name='list_current_user_messages'),
    path('unread/<str:username>/', views.list_unread_messages, name='list_unread_messages'),
    path('unread/', views.list_unread_messages, name='list_current_user_unread_messages'),
    path('mark-read/<int:message_id>/', views.mark_message_as_read, name='mark_message_as_read'),
    path('mark-all-read/', views.mark_all_messages_as_read, name='mark_all_messages_as_read'),
    path('threaded/<int:message_id>/', views.get_threaded_message, name='get_threaded_message'),
]
