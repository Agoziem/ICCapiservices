from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateformat import DateFormat
from django.conf import settings

DEBUG_MODE = settings.DEBUG_ENV


class Contact(models.Model):
    wa_id = models.CharField(max_length=50, unique=True)
    profile_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.profile_name or self.wa_id


MESSAGE_TYPES = [
    ("text", "Text"),
    ("image", "Image"),
    ("video", "Video"),
    ("audio", "Audio"),
    ("document", "Document"),
    ("sticker", "Sticker"),
]

MESSAGE_MODES = [
    ("received", "received"),
    ("sent", "sent"),
]


class WAMessage(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(
        "Contact", related_name="messages", on_delete=models.CASCADE
    )
    message_type = models.CharField(
        max_length=20, choices=MESSAGE_TYPES, default="text"
    )
    body = models.TextField(blank=True, default="")  # For text messages
    media_id = models.CharField(
        max_length=100, blank=True, default=""
    )  # For media messages
    mime_type = models.CharField(
        max_length=100, blank=True, default=""
    )  # For media messages
    filename = models.CharField(
        max_length=100, blank=True, default=""
    )  # For videos, documents
    animated = models.BooleanField(default=False)  # For stickers
    caption = models.TextField(blank=True, default="")  # For videos, images, documents
    link = models.URLField(
        blank=True, default="https://www.example.com"
    )  # For sent media messages
    message_mode = models.CharField(
        max_length=20, choices=MESSAGE_MODES, default="received"
    )
    seen = models.BooleanField(default=False)  # For received messages
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("sent", "Sent")],
        blank=True,
        default="pending",
    )  # Only for sent messages
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contact}: {self.message_type} ({self.message_mode})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if DEBUG_MODE and self.message_mode == "received":
            # Get the last message (which is this current one being saved)
            last_message = (
                WAMessage.objects.filter(contact=self.contact, message_mode="received")
                .order_by("-timestamp")
                .first()
            )

            if last_message:
                # Manually serialize the last message
                serialized_message = {
                    "id": last_message.pk,
                    "message_id": last_message.message_id,
                    "contact": last_message.contact.id,
                    "message_type": last_message.message_type,
                    "body": last_message.body,
                    "media_id": last_message.media_id,
                    "mime_type": last_message.mime_type,
                    "filename": last_message.filename,
                    "animated": last_message.animated,
                    "caption": last_message.caption,
                    "link": last_message.link,
                    "message_mode": last_message.message_mode,
                    "seen": last_message.seen,
                    "status": last_message.status,
                    "timestamp": DateFormat(last_message.timestamp).format(
                        "Y-m-d H:i:s"
                    ),
                }

                # Manually serialize the contact
                serialized_contact = {
                    "id": self.contact.id,
                    "wa_id": self.contact.wa_id,
                    "profile_name": self.contact.profile_name,
                    "last_message": self.get_last_message(
                        last_message
                    ),  # Use the last message directly
                    "unread_message_count": self.get_unread_message_count(self.contact),
                }

                print("am working now", serialized_contact)

                # Send the message to the appropriate WebSocket room
                room_name = "whatsappapi_messages"
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)( # type: ignore
                    room_name,
                    {
                        "type": "chat_message",
                        "operation": "create",
                        "contact": serialized_contact,
                        "message": serialized_message,
                    },
                )

                # Send an update to the general contacts room
                general_room_name = "whatsappapi_contacts"
                async_to_sync(channel_layer.group_send)( # type: ignore
                    general_room_name,
                    {
                        "type": "chat_message",
                        "operation": "create",
                        "contact": serialized_contact,
                    },
                )

    # Utility functions for manually serializing the contact
    def get_last_message(self, last_message):
        if last_message:
            return {
                "id": last_message.id,
                "message_id": last_message.message_id,
                "message_type": last_message.message_type,
                "body": last_message.body,
                "timestamp": DateFormat(last_message.timestamp).format("Y-m-d H:i:s"),
            }
        return None

    def get_unread_message_count(self, contact):
        return WAMessage.objects.filter(
            contact=contact, message_mode="received", seen=False
        ).count()


class Status(models.Model):
    message = models.ForeignKey(
        WAMessage, related_name="statuses", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=20)  # 'delivered', 'read', etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message.message_id} - {self.status} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id


# Tuple representing the message types (TEMPLATE_NAMES)
TEMPLATE_NAMES = [
    ("textonly", "Text Only"),
    ("textwithimage", "Text with Image"),
    ("textwithvideo", "Text with Video"),
    ("textwithaudio", "Text with Audio"),
    ("textwithdocument", "Text with Document"),
    ("textwithCTA", "Text with Call to Action (CTA)"),
]

MESSAGE_status = [("pending", "pending"), ("sent", "sent"), ("failed", "failed")]


# Model representing the template schema
class WATemplateSchema(models.Model):
    title = models.CharField(
        max_length=300, default="No Title", verbose_name="Message Title"
    )
    template = models.CharField(
        max_length=50,
        choices=TEMPLATE_NAMES,
        default="textonly",
        verbose_name="Template Type",
    )
    text = models.TextField(blank=True, null=True, verbose_name="Message Text")
    link = models.URLField(blank=True, null=True, verbose_name="Optional Link")
    status = models.CharField(
        max_length=255, blank=True, choices=MESSAGE_status, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.template} Template"

    class Meta:
        verbose_name = "WhatsApp Template"
        verbose_name_plural = "WhatsApp Templates"
