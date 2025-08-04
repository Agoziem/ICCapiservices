from typing import Optional
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ninja_jwt.authentication import JWTAuth

from ..models import Notification
from ..schemas import (
    NotificationSchema,
    NotificationListResponseSchema,
    CreateNotificationSchema,
    UnreadCountResponseSchema,
    UpdateNotificationSchema,
    MarkAsViewedSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
    PaginatedNotificationResponseSchema,
)


class NotificationPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/notifications", tags=["Notifications"])
class NotificationsController:

    @route.get("/", response=PaginatedNotificationResponseSchema, auth=JWTAuth())
    @paginate(NotificationPagination)
    def fetch_notifications(self, request):
        """Get all notifications with user-specific viewed status"""
        user = request.user
        notifications = Notification.objects.prefetch_related('users_viewed').order_by('-created_at')
        
        # Convert to list of schema objects with user-specific data
        return [
            NotificationSchema.from_orm_with_user(notification, user) 
            for notification in notifications
        ]

    @route.get("/user", response=PaginatedNotificationResponseSchema, auth=JWTAuth())
    @paginate(NotificationPagination)
    def fetch_user_notifications(self, request):
        """Get notifications for authenticated user"""
        user = request.user
        notifications = Notification.objects.prefetch_related('users_viewed').order_by('-created_at')
        
        # Convert to list of schema objects with user-specific data
        return [
            NotificationSchema.from_orm_with_user(notification, user) 
            for notification in notifications
        ]

    @route.get("/{notification_id}", response=NotificationSchema, auth=JWTAuth())
    def fetch_notification_by_id(self, request, notification_id: int):
        """Get a specific notification by ID with user-specific viewed status"""
        user = request.user
        notification = get_object_or_404(
            Notification.objects.prefetch_related('users_viewed'), 
            id=notification_id
        )
        return NotificationSchema.from_orm_with_user(notification, user)

    @route.post("/", response=NotificationSchema, auth=JWTAuth())
    def create_notification(self, request, payload: CreateNotificationSchema):
        """Create a new notification and send WebSocket update"""
        try:
            user = request.user
            notification_data = payload.model_dump()
            notification = Notification.objects.create(**notification_data)

            # Send WebSocket notification
            general_room_name = "notifications"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # type: ignore
                general_room_name,
                {
                    "type": "notification_message",
                    "action": "add",
                    "notification": NotificationSchema.from_orm_with_user(
                        notification, user
                    ).model_dump(),
                },
            )

            return NotificationSchema.from_orm_with_user(notification, user)
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{notification_id}", response=NotificationSchema, auth=JWTAuth()
    )
    def update_notification(
        self, request, notification_id: int, payload: UpdateNotificationSchema
    ):
        """Update an existing notification and send WebSocket update"""
        user = request.user
        notification = get_object_or_404(
            Notification.objects.prefetch_related('users_viewed'), 
            id=notification_id
        )

        notification_data = payload.model_dump(exclude_unset=True)
        for attr, value in notification_data.items():
            setattr(notification, attr, value)
        notification.save()

        # Send WebSocket notification
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "update",
                "notification": NotificationSchema.from_orm_with_user(
                    notification, user
                ).model_dump(),
            },
        )

        return NotificationSchema.from_orm_with_user(notification, user)

    @route.delete(
        "/{notification_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_notification(self, request, notification_id: int):
        """Delete a notification and send WebSocket update"""
        user = request.user
        notification = get_object_or_404(
            Notification.objects.prefetch_related('users_viewed'), 
            id=notification_id
        )

        # Get notification data before deletion for WebSocket
        notification_data = NotificationSchema.from_orm_with_user(notification, user).model_dump()

        # Send WebSocket notification before deletion
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "delete",
                "notification": notification_data,
            },
        )

        notification.delete()
        return {"message": "Notification deleted successfully"}

    @route.post("/{notification_id}/mark-viewed", response=NotificationSchema, auth=JWTAuth())
    def mark_notification_viewed(self, request, notification_id: int):
        """Mark a notification as viewed by the current user"""
        user = request.user
        notification = get_object_or_404(Notification, id=notification_id)
        
        # Add user to users_viewed if not already there
        if user not in notification.users_viewed.all():
            notification.users_viewed.add(user)

        # Send WebSocket notification
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "mark_viewed",
                "notification": NotificationSchema.from_orm_with_user(
                    notification, user
                ).model_dump(),
                "user_id": user.id,
            },
        )

        return NotificationSchema.from_orm_with_user(notification, user)

    @route.get("/unread/count", response=UnreadCountResponseSchema, auth=JWTAuth())
    def get_unread_count(self, request):
        """Get count of unread notifications for current user"""
        user = request.user
        # Count notifications where the user is NOT in users_viewed
        count = Notification.objects.exclude(users_viewed=user).count()
        return {"unread_count": count}

    @route.post("/mark-all-viewed", response=SuccessResponseSchema, auth=JWTAuth())
    def mark_all_viewed(self, request):
        """Mark all notifications as viewed for current user"""
        user = request.user
        
        # Get all notifications not viewed by this user
        unread_notifications = Notification.objects.exclude(users_viewed=user)
        updated_count = 0
        
        for notification in unread_notifications:
            notification.users_viewed.add(user)
            updated_count += 1

        # Send WebSocket notification for bulk update
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "mark_all_viewed",
                "updated_count": updated_count,
                "user_id": user.id,
            },
        )

        return {"message": f"Marked {updated_count} notifications as viewed"}
