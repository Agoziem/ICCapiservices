from rest_framework import serializers
from .models import *

class RecievedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceivedMessage
        fields = "__all__"

class SentMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SentMessage
        fields = "__all__"

class ContactSerializer(serializers.ModelSerializer):
    recieved_messages = RecievedMessageSerializer(many=True, read_only=True)
    sent_messages = SentMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'profile_name', 'recieved_messages', 'sent_messages']


class StatusSerializer(serializers.ModelSerializer):
    message = RecievedMessageSerializer()

    class Meta:
        model = Status
        fields = ['id', 'message', 'status', 'timestamp']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_id', 'payload']
