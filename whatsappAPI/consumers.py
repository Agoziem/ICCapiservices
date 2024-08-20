
"""
This Consumer will be able to send and receive whatsapmessages from the websocket
if it is a recieve operation, it will recieve the message from an http endpoint in the views, it will send the message to the group chat
if it is a send operation, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message and save the message to database, else it will return an error message
if it is a reply operation, it will contain the message_id , it is replying to, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message, else it will return an error message

"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from .models import Message, Contact, Status
import aiohttp
from django.utils.dateparse import parse_datetime

class WhatsappConsumer(AsyncWebsocketConsumer):
    # Functionality: WebSocket Connection Handling
    async def connect(self):
        self.contactwa_id = self.scope['url_route']['kwargs']['contactwa_id']
        self.room_group_name = f'whatsappapi_{self.contactwa_id}'

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

    # Functionality: Message Routing based on Operation Type
    async def receive(self, text_data):
        data = json.loads(text_data)
        operation = data.get('operation')
        message = data.get('message')
        
        if operation == 'receive':
            await self.handle_receive_message(message)
        elif operation == 'send':
            await self.handle_send_message(message)
        elif operation == 'reply':
            await self.handle_reply_message(message)
        elif operation == 'status_update':
            await self.handle_status_update(message)

    # Functionality: Handling Received Messages
    async def handle_receive_message(self, message):
        contact = await self.get_or_create_contact(message['wa_id'])
        await self.save_message(contact, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Functionality: Handling Sending Messages
    async def handle_send_message(self, message):
        response = await self.send_to_whatsapp_api(message)
        if response.status == 200:
            response_data = await response.json()
            message_id = response_data.get('messages', [{}])[0].get('id', '')

            contact = await self.get_or_create_contact(message['wa_id'])
            await self.save_message(contact, message, message_id)
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': 'Message sent successfully',
            }))
        else:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Failed to send message',
            }))

    # Functionality: Handling Replying to Messages
    async def handle_reply_message(self, message):
        response = await self.send_to_whatsapp_api(message)
        if response.status == 200:
            response_data = await response.json()
            message_id = response_data.get('messages', [{}])[0].get('id', '')

            contact = await self.get_or_create_contact(message['wa_id'])
            await self.save_message(contact, message, message_id)
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': 'Reply sent successfully',
            }))
        else:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Failed to send reply',
            }))

    # Functionality: Handling Status Updates
    async def handle_status_update(self, status_update):
        message_id = status_update.get('message_id')
        status = status_update.get('status')
        timestamp = status_update.get('timestamp')

        try:
            message = await self.get_message_by_id(message_id)
            Status.objects.create(
                message=message,
                status=status,
                timestamp=parse_datetime(timestamp)
            )
            await self.send(text_data=json.dumps({
                'status': 'success',
                'message': 'Status updated successfully',
            }))
        except Message.DoesNotExist:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': 'Message not found for status update',
            }))

    # Functionality: Sending Messages to WhatsApp API
    async def send_to_whatsapp_api(self, message):
        url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        data = {
            "messaging_product": "whatsapp",
            "to": message.get('to'),
            "type": message.get('type', 'text'),
            "text": {
                "body": message.get('body', '')
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                return response

    # Functionality: Saving Messages to Database
    async def save_message(self, contact, message, message_id=None):
        timestamp = parse_datetime(message.get('timestamp'))
        media_id = message.get('media_id')
        mime_type = message.get('mime_type')
        content = message.get('body', '')

        Message.objects.create(
            message_id=message_id or message.get('message_id'),
            contact=contact,
            message_type=message.get('type', 'text'),
            content=content,
            media_id=media_id,
            mime_type=mime_type,
            timestamp=timestamp
        )

    # Functionality: Contact Management
    async def get_or_create_contact(self, wa_id):
        contact, created = Contact.objects.get_or_create(wa_id=wa_id)
        return contact

    async def get_message_by_id(self, message_id):
        return Message.objects.get(message_id=message_id)

    # Functionality: Sending Messages to WebSocket Group
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


