from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/', fetch_notifications , name='notifications'),
    path('notifications/<int:id>/', fetch_notification_by_id, name='notification-detail'),
    path('notifications/create/', create_notification, name='notification-create'),
    path('notifications/<int:id>/update/', update_notification, name='notification-update'),
    path('notifications/<int:id>/delete/', delete_notification, name='notification-delete'),
]