from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('notifications/<str:username>/', views.list_notifications, name='list_notifications'),
    path('edit/<int:message_id>/', views.edit_message, name='edit_message'),
    path('history/<int:message_id>/', views.message_history, name='message_history'),
    path('user-edits/<str:username>/', views.user_message_edits, name='user_message_edits'),
]
