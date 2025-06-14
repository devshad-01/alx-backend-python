from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('notifications/<str:username>/', views.list_notifications, name='list_notifications'),
]
