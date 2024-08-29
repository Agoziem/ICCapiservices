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

{
    "contact": {
        "id": 15,
        "wa_id": "2348080982606",
        "profile_name": "Engr Gozzy",
        "recieved_messages": [
            {
                "id": 2,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEkFBQUIzOTIzODQ4M0UxNUM3RgA=",
                "message_type": "text",
                "body": "Thanks I love these update",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-26T21:33:11.299906Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 3,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEkZFQzBDOTYxREI3NUE1NEVGNQA=",
                "message_type": "text",
                "body": "i will like to have a word with you guys",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-26T21:34:50.102700Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 5,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYIDk0NkUxM0Q4QTQwRDkwNjc0ODU1OTg2RjUyMTg5RUFDAA==",
                "message_type": "text",
                "body": "Glory be to Jesus",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-26T21:48:57.498545Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 6,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEkU2REYxMTk2N0U1OTc0Rjg1OQA=",
                "message_type": "text",
                "body": "Thanks I love these update",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-26T22:00:08.598629Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 7,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEkREMjg2QjczMkExMUYzRDM1OAA=",
                "message_type": "text",
                "body": "i really love your Services",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-26T22:08:32.299345Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 19,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEjFGOUU2NjdCQUVFRUMxMjVCNQA=",
                "message_type": "text",
                "body": "Okay Sir",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-29T15:23:16.370103Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 20,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEkU5QzY5QjhDOEUwOTMyQjAyNwA=",
                "message_type": "text",
                "body": "thanks a lot for your support",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-29T15:42:58.384691Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 21,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEjNGRUExMDVDREMxQ0M2RUI1MgA=",
                "message_type": "text",
                "body": "I will definitely keep in touch",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-29T15:55:04.368718Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 22,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEjkzNDNCMDY0REM1Q0I0QzNEQwA=",
                "message_type": "text",
                "body": "thank you sir",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-29T16:03:39.273878Z",
                "message_mode": "received message",
                "contact": 15
            },
            {
                "id": 23,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABIYEjc4OTczQzQ2MEE3M0Y0ODc3OAA=",
                "message_type": "text",
                "body": "we love you Sir",
                "media_id": "",
                "mime_type": "",
                "timestamp": "2024-08-29T16:12:17.288078Z",
                "message_mode": "received message",
                "contact": 15
            }
        ],
        "sent_messages": [
            {
                "id": 1,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABEYEkJFREVEN0FDRDI5QjQyNUM4MgA=",
                "message_type": "text",
                "body": "Thanks alot for contacting Us",
                "link": "",
                "timestamp": "2024-08-27T02:49:13.652649Z",
                "message_mode": "sent message",
                "status": "sent",
                "contact": 15
            },
            {
                "id": 2,
                "message_id": "wamid.HBgNMjM0ODA4MDk4MjYwNhUCABEYEkM1RjhCQTY5MTgwRDk3N0RBNgA=",
                "message_type": "text",
                "body": "we will reach out to you soonest",
                "link": "",
                "timestamp": "2024-08-27T02:50:03.808100Z",
                "message_mode": "sent message",
                "status": "sent",
                "contact": 15
            }
        ]
    }
}
class ReceivedMessage(models.Model):
    message_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(Contact, related_name='recieved_messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    body = models.TextField(blank=True, null=True)  # For text messages
    media_id = models.CharField(max_length=100, blank=True, null=True) # For media messages
    mime_type = models.CharField(max_length=100, blank=True, null=True) # For media messages
    timestamp = models.DateTimeField(auto_now_add=True)
    message_mode = models.CharField(max_length=20, choices=MESSAGE_MODES, default='received message')

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
