from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateformat import DateFormat

class Contact(models.Model):
    wa_id = models.CharField(max_length=50, unique=True)
    profile_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.profile_name or self.wa_id


MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('sticker', 'Sticker'),
    ]

MESSAGE_MODES = [
    ('sent message', 'Sent message'),
    ('received message', 'Received message'),
]


class ReceivedMessage(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(Contact, related_name='recieved_messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    body = models.TextField(blank=True, null=True)  # For text messages
    media_id = models.CharField(max_length=100, blank=True, null=True) # For media messages
    mime_type = models.CharField(max_length=100, blank=True, null=True) # For media messages
    timestamp = models.DateTimeField(auto_now_add=True)
    message_mode = models.CharField(max_length=20, choices=MESSAGE_MODES, default='received message')
    seen = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.contact}: {self.message_type}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Fetch all received messages for this contact
        all_received_messages = list(self.contact.recieved_messages.values(
            'id', 'message_id', 'message_type', 'body', 'media_id', 'mime_type', 'timestamp', 'message_mode'
        ))

        # Convert the 'timestamp' field from datetime to string
        for message in all_received_messages:
            if 'timestamp' in message:
                message['timestamp'] = DateFormat(message['timestamp']).format('Y-m-d H:i:s')

        # Fetch all sent messages for this contact
        all_sent_messages = list(self.contact.sent_messages.values(
            'id', 'message_id', 'message_type', 'body', 'link', 'timestamp', 'message_mode', 'status'
        ))
        # Convert the 'timestamp' field from datetime to string
        for message in all_sent_messages:
            if 'timestamp' in message:
                message['timestamp'] = DateFormat(message['timestamp']).format('Y-m-d H:i:s')

        # Prepare the message data
        received_message_contact = {
            'id': self.contact.id,
            'wa_id': self.contact.wa_id,
            'profile_name': self.contact.profile_name,
            'recieved_messages': all_received_messages,
            'sent_messages': all_sent_messages
        }
        
        # Determine the room name
        room_name = "whatsappapi_general"
        
        # Get the channel layer and send the message
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                'type': 'chat_message',
                'contact': received_message_contact
            }
        )


class SentMessage(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(Contact, related_name='sent_messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    body = models.TextField(blank=True, null=True)  # For text messages
    link = models.URLField(blank=True, null=True)  # For media messages
    timestamp = models.DateTimeField(auto_now_add=True)
    message_mode = models.CharField(max_length=20, choices=MESSAGE_MODES, default='sent message')
    status = models.CharField(max_length=20, choices=[("pending","pending"),("sent","sent")], default='pending')  # 'sent', 'delivered', 'read', etc.
    


class Status(models.Model):
    message = models.ForeignKey(ReceivedMessage, related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # 'delivered', 'read', etc.
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.message.message_id} - {self.status}"

    def __str__(self):
        return f"{self.contact}: {self.message_type}"

class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id
