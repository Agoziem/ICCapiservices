from typing import Dict, Any, List
from ninja_extra import api_controller, route
from ninja_extra.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
import requests

from ..models import Contact, WAMessage, Status, WebhookEvent
from ..schemas import (
    WebhookPayloadSchema,
    SendMessageSchema,
    TemplateMessageSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
    CreateWebhookEventSchema,
    WebhookEventSchema,
)


@api_controller(
    "/whatsapp/webhook", tags=["WhatsApp Webhook Integration"], permissions=[AllowAny]
)
class WhatsAppWebhookController:

    @route.post("/receive", response=Dict[str, str])
    def whatsapp_webhook(self, payload: WebhookPayloadSchema):
        """Webhook for receiving WhatsApp messages and statuses from Meta's WhatsApp Business API"""
        try:
            webhook_data = payload.model_dump()

            # Store the entire payload for reference
            entry = webhook_data.get("entry", [{}])[0]
            event_id = entry.get("id")

            if event_id:
                # Create webhook event record
                WebhookEvent.objects.get_or_create(
                    event_id=event_id, defaults={"payload": webhook_data}
                )

            # Process changes from the webhook
            changes = entry.get("changes", [])

            for change in changes:
                value = change.get("value", {})

                # Handle incoming messages
                messages = value.get("messages", [])
                for message_data in messages:
                    self._process_incoming_message(message_data)

                # Handle message statuses (delivery confirmations, read receipts, etc.)
                statuses = value.get("statuses", [])
                for status_data in statuses:
                    self._process_message_status(status_data)

            return {"status": "success"}

        except Exception as e:
            return {"error": str(e)}

    @route.post("/send-message/{contact_id}", response=Dict[str, Any])
    def send_message(self, contact_id: int, payload: SendMessageSchema):
        """Send a message to a WhatsApp contact"""
        try:
            contact = get_object_or_404(Contact, id=contact_id)
            message_data = payload.model_dump()

            # Prepare WhatsApp API request
            whatsapp_payload = {
                "messaging_product": "whatsapp",
                "to": contact.wa_id,
                "type": message_data["message_type"],
            }

            # Add message content based on type
            if message_data["message_type"] == "text":
                whatsapp_payload["text"] = {"body": message_data.get("body", "")}
            else:
                # Handle media messages
                media_type = message_data["message_type"]
                whatsapp_payload[media_type] = {}

                if message_data.get("media_id"):
                    whatsapp_payload[media_type]["id"] = message_data["media_id"]
                elif message_data.get("link"):
                    whatsapp_payload[media_type]["link"] = message_data["link"]

                if message_data.get("caption"):
                    whatsapp_payload[media_type]["caption"] = message_data["caption"]

            # Send to WhatsApp API
            response = self._send_to_whatsapp_api(whatsapp_payload)

            if response and response.get("messages"):
                # Create local message record
                message_id = response["messages"][0]["id"]
                wa_message = WAMessage.objects.create(
                    message_id=message_id,
                    contact=contact,
                    message_type=message_data["message_type"],
                    body=message_data.get("body", ""),
                    media_id=message_data.get("media_id", ""),
                    caption=message_data.get("caption", ""),
                    link=message_data.get("link", "https://www.example.com"),
                    message_mode="sent",
                    status="sent",
                )

                return {"status": "success", "message_id": message_id}
            else:
                return {"error": "Failed to send message"}

        except Exception as e:
            return {"error": str(e)}

    @route.post("/send-template", response=Dict[str, Any])
    def send_template_message(self, payload: TemplateMessageSchema):
        """Send a template message to a WhatsApp number"""
        try:
            template_data = payload.model_dump()

            # Prepare WhatsApp API request for template
            whatsapp_payload = {
                "messaging_product": "whatsapp",
                "to": template_data["to_phone_number"],
                "type": "template",
                "template": {
                    "name": template_data["template_name"],
                    "language": {"code": template_data["language_code"]},
                },
            }

            # Send to WhatsApp API
            response = self._send_to_whatsapp_api(whatsapp_payload)

            if response and response.get("messages"):
                return {
                    "status": "success",
                    "message_id": response["messages"][0]["id"],
                }
            else:
                return {"error": "Failed to send template message"}

        except Exception as e:
            return {"error": str(e)}

    def _process_incoming_message(self, message_data):
        """Process incoming message from webhook"""
        try:
            with transaction.atomic():
                # Get or create contact
                from_number = message_data.get("from")
                profile_name = message_data.get("profile", {}).get("name", "")

                contact, created = Contact.objects.get_or_create(
                    wa_id=from_number, defaults={"profile_name": profile_name}
                )

                # Update profile name if it changed
                if (
                    not created
                    and profile_name
                    and contact.profile_name != profile_name
                ):
                    contact.profile_name = profile_name
                    contact.save()

                # Create message record
                message_id = message_data.get("id")
                message_type = message_data.get("type", "text")
                timestamp_str = message_data.get("timestamp")

                # Parse timestamp
                if timestamp_str:
                    timestamp = datetime.fromtimestamp(int(timestamp_str))
                else:
                    timestamp = datetime.now()

                # Extract message content based on type
                body = ""
                media_id = ""
                mime_type = ""
                filename = ""
                caption = ""
                animated = False

                if message_type == "text":
                    body = message_data.get("text", {}).get("body", "")
                elif message_type in ["image", "video", "audio", "document"]:
                    media_info = message_data.get(message_type, {})
                    media_id = media_info.get("id", "")
                    mime_type = media_info.get("mime_type", "")
                    filename = media_info.get("filename", "")
                    caption = media_info.get("caption", "")
                elif message_type == "sticker":
                    sticker_info = message_data.get("sticker", {})
                    media_id = sticker_info.get("id", "")
                    mime_type = sticker_info.get("mime_type", "")
                    animated = sticker_info.get("animated", False)

                # Create or update message
                wa_message, created = WAMessage.objects.get_or_create(
                    message_id=message_id,
                    defaults={
                        "contact": contact,
                        "message_type": message_type,
                        "body": body,
                        "media_id": media_id,
                        "mime_type": mime_type,
                        "filename": filename,
                        "caption": caption,
                        "animated": animated,
                        "message_mode": "received",
                        "timestamp": timestamp,
                    },
                )

        except Exception as e:
            print(f"Error processing incoming message: {e}")

    def _process_message_status(self, status_data):
        """Process message status update from webhook"""
        try:
            message_id = status_data.get("id")
            status_type = status_data.get("status")
            timestamp_str = status_data.get("timestamp")

            # Find the message
            try:
                wa_message = WAMessage.objects.get(message_id=message_id)

                # Update message status
                wa_message.status = status_type
                wa_message.save()

                # Create status record
                if timestamp_str:
                    timestamp = datetime.fromtimestamp(int(timestamp_str))
                else:
                    timestamp = datetime.now()

                Status.objects.create(
                    message=wa_message, status=status_type, timestamp=timestamp
                )

            except WAMessage.DoesNotExist:
                print(f"Message with ID {message_id} not found")

        except Exception as e:
            print(f"Error processing message status: {e}")

    def _send_to_whatsapp_api(self, payload):
        """Send request to WhatsApp Business API"""
        try:
            url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
                "Content-Type": "application/json",
            }

            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"WhatsApp API error: {response.text}")
                return None

        except Exception as e:
            print(f"Error sending to WhatsApp API: {e}")
            return None
