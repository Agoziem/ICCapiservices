import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
from .serializers import NotificationSerializer
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'notifications'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        notification_id = data.get('id')

        if action == 'mark_viewed':
            await self.mark_notification_as_viewed(notification_id)
        elif action == 'add':
            await self.add_notification(data)
        elif action == 'update':
            await self.update_notification(notification_id, data)
        elif action == 'delete':
            await self.delete_notification(notification_id)

    async def mark_notification_as_viewed(self, notification_id):
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        notification.viewed = True
        await sync_to_async(notification.save)()
        await self.notify_group('update', notification_id)

    async def add_notification(self, data):
        new_notification_data = data.get('notification')
        serializer = NotificationSerializer(data=new_notification_data)
        if serializer.is_valid():
            notification = await sync_to_async(serializer.save)()
            await self.notify_group('add', notification.id)
        else:
            await self.send(text_data=json.dumps(serializer.errors))

    async def update_notification(self, notification_id, data):
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        update_notification_data = data.get('notification')
        serializer = NotificationSerializer(notification, data=update_notification_data)
        if serializer.is_valid():
            await sync_to_async(serializer.save)()
            await self.notify_group('update', notification_id)
        else:
            await self.send(text_data=json.dumps(serializer.errors))

    async def delete_notification(self, notification_id):
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        await sync_to_async(notification.delete)()
        await self.notify_group('delete', notification_id)

    async def notify_group(self, action, notification_id):
        notification = await sync_to_async(Notification.objects.get)(id=notification_id)
        serializer = NotificationSerializer(notification)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'action': action,
                'notification': serializer.data
            }
        )

    async def notification_message(self, event):
        action = event['action']
        notification = event['notification']

        await self.send(text_data=json.dumps({
            'action': action,
            'notification': notification
        }))
