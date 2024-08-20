from rest_framework import serializers
from .models import Contact, Message, Status, WebhookEvent

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'profile_name']

class MessageSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = Message
        fields = ['id', 'message_id', 'contact', 'message_type', 'content', 'media_id', 'mime_type', 'timestamp']

class StatusSerializer(serializers.ModelSerializer):
    message = MessageSerializer()

    class Meta:
        model = Status
        fields = ['id', 'message', 'status', 'timestamp']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_id', 'payload']
