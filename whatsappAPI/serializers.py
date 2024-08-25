from rest_framework import serializers
from .models import *

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'profile_name']

class RecievedMessageSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = ReceivedMessage
        fields = "__all__"

class SentMessageSerializer(serializers.ModelSerializer):
    contact = ContactSerializer()

    class Meta:
        model = SentMessage
        fields = "__all__"

class StatusSerializer(serializers.ModelSerializer):
    message = RecievedMessageSerializer()

    class Meta:
        model = Status
        fields = ['id', 'message', 'status', 'timestamp']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_id', 'payload']
