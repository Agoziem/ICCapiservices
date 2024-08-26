
"""
This Consumer will be able to send and receive whatsapmessages from the websocket
if it is a recieve operation, it will recieve the message from an http endpoint in the views, it will send the message to the group chat
if it is a send operation, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message and save the message to database, else it will return an error message
if it is a reply operation, it will contain the message_id , it is replying to, it will send the message to the whatsapp api to send the message to the user , then return the response, if the response is 200, it will return a success message, else it will return an error message

"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.dateparse import parse_datetime

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

    # ----------------------------------------------------------------
    # Functionality: Sending Messages to WebSocket Group
    # ----------------------------------------------------------------
    async def chat_message(self, event):
        contact = event['contact']
        await self.send(text_data=json.dumps({
            'contact': contact
        }))

