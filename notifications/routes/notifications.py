from typing import Optional
from ninja_extra import api_controller, route
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
    UpdateNotificationSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/notifications", tags=["Notifications"])
class NotificationsController:

    @route.get("/", response=list[NotificationSchema])
    def fetch_notifications(self):
        """Get all notifications"""
        notifications = Notification.objects.all()
        return notifications

    @route.get("/{notification_id}", response=NotificationSchema)
    def fetch_notification_by_id(self, notification_id: int):
        """Get a specific notification by ID"""
        notification = get_object_or_404(Notification, id=notification_id)
        return notification

    @route.post("/", response=NotificationSchema, auth=JWTAuth())
    def create_notification(self, payload: CreateNotificationSchema):
        """Create a new notification and send WebSocket update"""
        try:
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
                    "notification": NotificationSchema.model_validate(
                        notification
                    ).model_dump(),
                },
            )

            return notification
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{notification_id}", response=NotificationSchema, auth=JWTAuth()
    )
    def update_notification(
        self, notification_id: int, payload: UpdateNotificationSchema
    ):
        """Update an existing notification and send WebSocket update"""
        notification = get_object_or_404(Notification, id=notification_id)

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
                "notification": NotificationSchema.model_validate(
                    notification
                ).model_dump(),
            },
        )

        return notification

    @route.delete(
        "/{notification_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_notification(self, notification_id: int):
        """Delete a notification and send WebSocket update"""
        notification = get_object_or_404(Notification, id=notification_id)

        # Get notification data before deletion for WebSocket
        notification_data = NotificationSchema.model_validate(notification).model_dump()

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

    @route.post("/{notification_id}/mark-viewed", response=NotificationSchema)
    def mark_notification_viewed(self, notification_id: int):
        """Mark a notification as viewed"""
        notification = get_object_or_404(Notification, id=notification_id)
        notification.viewed = True
        notification.save()

        # Send WebSocket notification
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "update",
                "notification": NotificationSchema.model_validate(
                    notification
                ).model_dump(),
            },
        )

        return notification

    @route.get("/unread/count")
    def get_unread_count(self):
        """Get count of unread notifications"""
        count = Notification.objects.filter(viewed=False).count()
        return {"unread_count": count}

    @route.post("/mark-all-viewed", response=SuccessResponseSchema)
    def mark_all_viewed(self):
        """Mark all notifications as viewed"""
        updated_count = Notification.objects.filter(viewed=False).update(viewed=True)

        # Send WebSocket notification for bulk update
        general_room_name = "notifications"
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(  # type: ignore
            general_room_name,
            {
                "type": "notification_message",
                "action": "mark_all_viewed",
                "updated_count": updated_count,
            },
        )

        return {"message": f"Marked {updated_count} notifications as viewed"}
