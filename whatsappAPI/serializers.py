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
                'id': last_message.pk,
                'message_id': last_message.message_id,
                'message_type': last_message.message_type,
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

class WATemplateSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = WATemplateSchema
        fields = ['id', 'template', 'text', 'link', 'created_at', 'title', 'status']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        validated_data['status'] = 'sent' 
        return super().create(validated_data)



# Serializer for documenting the webhook payload
class WebhookPayloadSerializer(serializers.Serializer):
    entry = serializers.ListField(child=serializers.DictField(), help_text="List of entry objects")
    
# Serializer for sending messages
class SendMessageSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(choices=['text', 'image', 'audio', 'document', 'video'], default='text')
    body = serializers.CharField(required=False, help_text="Message text body")
    media_id = serializers.CharField(required=False, help_text="ID of media for non-text messages")
    link = serializers.URLField(required=False, help_text="URL for media messages")
    caption = serializers.CharField(required=False, help_text="Caption for media messages")
    message_mode = serializers.CharField(required=False, help_text="Message mode")
    timestamp = serializers.CharField(required=False, help_text="Message timestamp")
    
# Serializer for sending template messages
class TemplateMessageSerializer(serializers.Serializer):
    to_phone_number = serializers.CharField(help_text="Recipient's phone number with country code")
    template_name = serializers.CharField(help_text="Name of the template to use")
    language_code = serializers.CharField(default="en_US", help_text="Language code for the template")