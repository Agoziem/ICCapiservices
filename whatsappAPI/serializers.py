from rest_framework import serializers
from .models import *
from django.utils.dateformat import DateFormat


class WAMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WAMessage
        fields = "__all__"

class ContactSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    unread_message_count = serializers.SerializerMethodField()

    class Meta:
        model = Contact
        fields = ['id', 'wa_id', 'profile_name', 'last_message', 'unread_message_count']

    # Method to get the last message for the contact
    def get_last_message(self, obj):
        # Get the most recent message (by timestamp) for this contact
        last_message = WAMessage.objects.filter(contact=obj).order_by('-timestamp').first()
        if last_message:
            return {
                'id':last_message.id,
                'message_id': last_message.message_id,
                'message_type':last_message.message_type,
                'body': last_message.body,
                'timestamp': DateFormat(last_message.timestamp).format('Y-m-d H:i:s')
            }
        return None

    # Method to get the number of unread messages for the contact
    def get_unread_message_count(self, obj):
        return WAMessage.objects.filter(contact=obj,message_mode='received', seen=False).count()


class StatusSerializer(serializers.ModelSerializer):
    message = WAMessage()
    class Meta:
        model = Status
        fields = ['id', 'message', 'status', 'timestamp']

class WebhookEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebhookEvent
        fields = ['id', 'event_id', 'payload']
