from django.db import models

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
    timestamp = models.DateTimeField()
    message_mode = models.CharField(max_length=20, choices=MESSAGE_MODES, default='received message')

    def __str__(self):
        return f"{self.contact}: {self.message_type}"

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
    timestamp = models.DateTimeField()

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
