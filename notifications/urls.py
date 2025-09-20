from django.urls import path
from . import views

urlpatterns = [
    # Basic CRUD operations
    path('', views.get_all_notifications, name='get_all_notifications'),
    path('create/', views.create_notification, name='create_notification'),
    path('get/<int:notification_id>/', views.get_notification_by_id, name='get_notification_by_id'),
    path('update/<int:notification_id>/', views.update_notification, name='update_notification'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    
    # User-specific operations
    path('user/<int:user_id>/unread/', views.get_unread_notifications, name='get_unread_notifications'),
    path('user/<int:user_id>/sent/', views.get_user_sent_notifications, name='get_user_sent_notifications'),
    
    # Notification management
    path('mark-read/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('remove-user/', views.remove_user_from_notification, name='remove_user_from_notification'),
]