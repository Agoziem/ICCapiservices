
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Contact, WAMessage
from channels.db import database_sync_to_async
from .serializers import ContactSerializer  # Ensure you have this serializer in place



class WAMessagesConsumer(AsyncWebsocketConsumer):
    # ----------------------------------------------------------------
    # Functionality: WebSocket Connection Handling
    # ----------------------------------------------------------------
    async def connect(self):
        self.room_group_name = f'whatsappapi_messages'
        # Join room group
        print('connected to contacts Socket')
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
        print('disconnected to contacts Socket')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
    # ----------------------------------------------------------------
    # Functionality: Sending Messages to WebSocket Group
    # ----------------------------------------------------------------
    async def chat_message(self, event):
        operation = event['operation']
        contact = event['contact']
        message = event['message']
        await self.send(text_data=json.dumps({
            'operation': operation,
            'contact': contact,
            'message': message
        }))





class WAContactsConsumer(AsyncWebsocketConsumer):
    # ----------------------------------------------------------------
    # Functionality: WebSocket Connection Handling
    # ----------------------------------------------------------------
    async def connect(self):
        self.room_group_name = 'whatsappapi_contacts'
        print('Connected to messages Socket')
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # ----------------------------------------------------------------
    # Functionality: Disconnecting from WebSocket
    # ----------------------------------------------------------------
    async def disconnect(self, close_code):
        # Leave room group
        print('Disconnected from messages Socket')
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # ----------------------------------------------------------------
    # Sending a chat message to WebSocket
    # ----------------------------------------------------------------
    async def chat_message(self, event):
        contact = event['contact']
        operation = event['operation']
        await self.send(text_data=json.dumps({
            'operation': operation,
            'contact': contact
        }))

    # ----------------------------------------------------------------
    # Functionality: Receiving data from WebSocket
    # ----------------------------------------------------------------
    async def receive(self, text_data):
        data = json.loads(text_data)
        operation = data.get('operation')
        contactdata = data.get('contact')            
        if operation == 'update_seen_status':
            await self.update_seen_status(contactdata)

    # ----------------------------------------------------------------
    # Helper: Fetch contact synchronously in an async context
    # ----------------------------------------------------------------
    @database_sync_to_async
    def get_contact(self, contact_id):
        try:
            return Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return None

    # ----------------------------------------------------------------
    # Helper: Mark all messages as seen for a contact
    # ----------------------------------------------------------------
    @database_sync_to_async
    def mark_all_messages_as_seen(self, contact):
        WAMessage.objects.filter(contact=contact, seen=False).update(seen=True)

    # ----------------------------------------------------------------
    # Helper: Serialize contact and message information
    # ----------------------------------------------------------------
    @database_sync_to_async
    def serialize_contact(self, contact):
        serializer = ContactSerializer(contact)
        return serializer.data

    # ----------------------------------------------------------------
    # Functionality: Update Seen Status
    # ----------------------------------------------------------------
    async def update_seen_status(self, data):
        contact_id = data.get('id')  # WhatsApp ID of the contact
        contact = await self.get_contact(contact_id)

        if contact:
            # Mark all messages as seen
            await self.mark_all_messages_as_seen(contact)

            # Serialize the updated contact information
            updated_contact_data = await self.serialize_contact(contact)

            # Notify other WebSocket users about the updated seen status
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'operation': 'update_seen_status',
                    'contact': updated_contact_data  # Send the updated serialized contact data
                }
            )
        else:
            await self.send(text_data=json.dumps({'error': 'Contact not found'}))


   


