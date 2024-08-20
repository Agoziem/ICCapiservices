from django.db import models

class Contact(models.Model):
    wa_id = models.CharField(max_length=50, unique=True)
    profile_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.profile_name or self.wa_id

class Message(models.Model):
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('sticker', 'Sticker'),
    ]
    
    message_id = models.CharField(max_length=100, unique=True)
    contact = models.ForeignKey(Contact, related_name='messages', on_delete=models.CASCADE)
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField(blank=True, null=True)  # For text messages
    media_id = models.CharField(max_length=100, blank=True, null=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.contact}: {self.message_type}"

class Status(models.Model):
    message = models.ForeignKey(Message, related_name='statuses', on_delete=models.CASCADE)
    status = models.CharField(max_length=20)  # 'delivered', 'read', etc.
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.message.message_id} - {self.status}"

class WebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event_id
