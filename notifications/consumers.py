import json
from channels.generic.websocket import AsyncWebsocketConsumer

from notifications.schemas import NotificationSchema
from .models import Notification
from asgiref.sync import sync_to_async


# {
#   "action": "add" | "update" | "delete" | "mark_viewed",
#   "notification": {
#     "id": 1,
#     "title": "New Message",
#     "message": "You have a new message",
#     "viewed": false,
#     "updated_at": "2024-10-05T12:34:56Z",
#     "created_at": "2024-10-05T12:34:56Z"
#   }
# }


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "notifications"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        notification_data = data.get("notification")
        notification_id = notification_data.get("id") if notification_data else None

        # Process actions based on the action type
        if action == "mark_viewed" and notification_id:
            await self.mark_notification_as_viewed(notification_id)
        # elif action == 'add' and notification_data:
        #     await self.add_notification(notification_data)
        # elif action == 'update' and notification_id and notification_data:
        #     await self.update_notification(notification_id, notification_data)
        # elif action == 'delete' and notification_id:
        #     await self.delete_notification(notification_id)

    async def mark_notification_as_viewed(self, notification_id):
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        notification.viewed = True
        await sync_to_async(notification.save)()
        await self.notify_group("mark_viewed", notification)

    # async def add_notification(self, notification_data):
    #     serializer = NotificationSerializer(data=notification_data)
    #     if serializer.is_valid():
    #         notification = await sync_to_async(serializer.save)()
    #         await self.notify_group('add', notification)
    #     else:
    #         await self.send(text_data=json.dumps(serializer.errors))

    # async def update_notification(self, notification_id, notification_data):
    #     notification = await sync_to_async(Notification.objects.get)(id=notification_id)
    #     serializer = NotificationSerializer(notification, data=notification_data)
    #     if serializer.is_valid():
    #         await sync_to_async(serializer.save)()
    #         await self.notify_group('update', notification)
    #     else:
    #         await self.send(text_data=json.dumps(serializer.errors))

    # async def delete_notification(self, notification_id):
    #     notification = await sync_to_async(Notification.objects.get)(id=notification_id)
    #     await sync_to_async(notification.delete)()
    #     await self.notify_group('delete', notification)

    async def notify_group(self, action, notification):
        """Send message to the group in the desired format"""
        serialized_notification = NotificationSchema.model_validate(
            notification
        ).model_dump()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "notification_message",
                "action": action,
                "notification": serialized_notification,
            },
        )

    async def notification_message(self, event):
        action = event["action"]
        notification = event["notification"]

        # Send the message in the frontend-friendly format
        await self.send(
            text_data=json.dumps({"action": action, "notification": notification})
        )
