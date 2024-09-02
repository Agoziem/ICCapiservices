
"""
This Consumer will be able to send and receive whatsapmessages from the websocket
if it is a recieve operation, it will recieve the message from an http endpoint in the views, it will send the message to the group chat
if it is a send operation, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message and save the message to database, else it will return an error message
if it is a reply operation, it will contain the message_id , it is replying to, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message, else it will return an error message

"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Contact, ReceivedMessage
from channels.db import database_sync_to_async


class WhatsappConsumer(AsyncWebsocketConsumer):
    # ----------------------------------------------------------------
    # Functionality: WebSocket Connection Handling
    # ----------------------------------------------------------------
    async def connect(self):
        self.contactwa_id = self.scope['url_route']['kwargs']['contactwa_id']
        self.room_group_name = f'whatsappapi_{self.contactwa_id}'
        print(self.room_group_name)
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # ----------------------------------------------------------------
    # Functionality:  disconnecting from WebSocket
    # ----------------------------------------------------------------
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    # ----------------------------------------------------------------
    # Functionality: Sending Messages to WebSocket Group
    # ----------------------------------------------------------------
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))


class GeneralWhatsappConsumer(AsyncWebsocketConsumer):
    # ----------------------------------------------------------------
    # Functionality: WebSocket Connection Handling
    # ----------------------------------------------------------------
    async def connect(self):
        self.room_group_name = 'whatsappapi_general'
        # Join room group
        print("connected")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # ----------------------------------------------------------------
    # Functionality:  disconnecting from WebSocket
    # ----------------------------------------------------------------
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        contact = await self.get_contact(data['wa_id'])

        if action == 'update_seen_status':
            await self.update_seen_status(data, contact)

    # ----------------------------------------------------------------
    # Functionality: Update Seen Status
    # ----------------------------------------------------------------
    async def update_seen_status(self, data, contact):
        message_ids = data['message_ids']

        # Update seen status of messages asynchronously
        for message_id in message_ids:
            await self.mark_message_as_seen(contact, message_id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'update_status',
                "message": {
                    "message_ids": message_ids,
                    'contact_id': contact.id,
                    "success": "true"
                },
            }
        )

    # ----------------------------------------------------------------
    # Helper: Fetch contact synchronously in an async context
    # ----------------------------------------------------------------
    @database_sync_to_async
    def get_contact(self, wa_id):
        return Contact.objects.get(wa_id=wa_id)

    # ----------------------------------------------------------------
    # Helper: Mark message as seen synchronously in an async context
    # ----------------------------------------------------------------
    @database_sync_to_async
    def mark_message_as_seen(self, contact, message_id):
        message = ReceivedMessage.objects.get(contact=contact, message_id=message_id)
        message.seen = True
        message.save()

      # ----------------------------------------------------------------
    # Functionality: Sending Messages to WebSocket Group
    # ----------------------------------------------------------------
    async def chat_message(self, event):
        contact = event['contact']
        await self.send(text_data=json.dumps({
            'operation': 'chat_message',
            'contact': contact
        }))

    # ----------------------------------------------------------------
    # Functionality: Update Seen Status
    # ----------------------------------------------------------------
    async def update_status(self, event):
        message = event['message']
        print("sending back the upodate message",message)
        await self.send(text_data=json.dumps({
            'operation': 'update_status',
            'message': message
        }))


