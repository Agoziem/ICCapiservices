import json
from channels.generic.websocket import AsyncWebsocketConsumer

from emails.schemas import EmailSchema
from .models import Email
from channels.db import database_sync_to_async


class EmailConsumer(AsyncWebsocketConsumer):
    # WebSocket connection handling
    async def connect(self):
        self.room_group_name = "emailapi"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Sending messages to WebSocket Group
    async def chat_message(self, event):
        message = event["message"]
        operation = event["operation"]
        await self.send(
            text_data=json.dumps({"message": message, "operation": operation})
        )

    # Functionality: Handling incoming messages via WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        operation = data.get("operation")
        message = data.get("message")

        if operation == "create":
            await self.create_email(message)
        elif operation == "update":
            await self.update_read_status(message)
        else:
            await self.send(text_data=json.dumps({"error": "unstructured data"}))

    # ----------------------------------------------------------------
    # Functionality: Create an Email entry
    # ----------------------------------------------------------------
    @database_sync_to_async
    def create_email_in_db(self, email_data):
        return Email.objects.create(
            organization=email_data["organization"],
            name=email_data["name"],
            email=email_data["email"],
            subject=email_data["subject"],
            message=email_data["message"],
        )

    async def create_email(self, data):
        try:
            email = await self.create_email_in_db(data)
            serialized_email = EmailSchema.model_validate(email).model_dump()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "operation": "create",
                    "message": serialized_email,
                },
            )
        except Exception as e:
            await self.send(text_data=json.dumps({"error": str(e)}))

    # ----------------------------------------------------------------
    # Functionality: Update the read status of an Email
    # ----------------------------------------------------------------
    @database_sync_to_async
    def update_email_read_status(self, email_id, read_status):
        try:
            email = Email.objects.get(id=email_id)
            email.read = True
            email.save()
            serialized_email = EmailSchema.model_validate(email).model_dump()
            return serialized_email
        except Email.DoesNotExist:
            return None

    async def update_read_status(self, data):
        email_id = data.get("id")
        read_status = data.get("read")  # Default to False if not provided

        email = await self.update_email_read_status(email_id, read_status)

        if email:
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "operation": "update", "message": email},
            )
        else:
            await self.send(text_data=json.dumps({"error": "Email not found"}))
