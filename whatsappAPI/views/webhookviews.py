from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Contact, WAMessage, Status, WebhookEvent
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateparse import parse_datetime
from django.conf import settings
import requests
from rest_framework import status
from ..serializers import WAMessageSerializer, ContactSerializer
from datetime import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers

# Serializer for documenting the webhook payload
class WebhookPayloadSerializer(serializers.Serializer):
    entry = serializers.ListField(child=serializers.DictField(), help_text="List of entry objects")
    
# Serializer for sending messages
class SendMessageSerializer(serializers.Serializer):
    message_type = serializers.ChoiceField(choices=['text', 'image', 'audio', 'document', 'video'], default='text')
    body = serializers.CharField(required=False, help_text="Message text body")
    media_id = serializers.CharField(required=False, help_text="ID of media for non-text messages")
    link = serializers.URLField(required=False, help_text="URL for media messages")
    
# Serializer for sending template messages
class TemplateMessageSerializer(serializers.Serializer):
    to_phone_number = serializers.CharField(help_text="Recipient's phone number with country code")
    template_name = serializers.CharField(help_text="Name of the template to use")
    language_code = serializers.CharField(default="en_US", help_text="Language code for the template")



@swagger_auto_schema(
    method='post',
    operation_description="Webhook for receiving WhatsApp messages and statuses from Meta's WhatsApp Business API",
    request_body=WebhookPayloadSerializer,
    responses={
        200: openapi.Response(description="Success")
    }
)
@api_view(['POST'])
def whatsapp_webhook(request):
    payload = request.data

    # Store the entire payload for reference
    entry = payload.get('entry', [{}])[0]
    event_id = entry.get('id')
    WebhookEvent.objects.get_or_create(event_id=event_id, defaults={'payload': payload})
    # Start a database transaction
    with transaction.atomic():
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})

        # Handle contacts
        for contact_data in value.get('contacts', []):
            contact, created = Contact.objects.get_or_create(
                wa_id=contact_data['wa_id'],
                defaults={'profile_name': contact_data.get('profile', {}).get('name', '')}
            )
            # Handle messages
            for message_data in value.get('messages', []):
                try:
                    recieved_message = WAMessage.objects.create(
                        message_id=message_data['id'],
                        contact=contact,
                        message_type=message_data['type'],
                        body=message_data.get('text', {}).get('body', ''),
                        media_id=message_data.get(message_data['type'], {}).get('id', ''),
                        mime_type=message_data.get(message_data['type'], {}).get('mime_type', ''),
                        caption=message_data.get(message_data['type'], {}).get('caption', ''),
                        filename=message_data.get(message_data['type'], {}).get('filename', ''),
                    )
                    serialized_message = WAMessageSerializer(recieved_message).data

                    # Send the message to the appropriate WebSocket room
                    room_name = f'whatsappapi_messages'
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        room_name,
                        {
                            'type': 'chat_message',
                            'operation':"create",
                            'contact': contact,
                            'message': serialized_message
                        }
                    )
                except KeyError as e:
                    print(f"Missing key in message data: {e}")
                except Exception as e:
                    print(f"Error processing message: {e}")

            # Serialize the contact
            serialized_contact = ContactSerializer(contact).data
            general_room_name = 'whatsappapi_contacts'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                general_room_name,
                {
                    'type': 'chat_message',
                    'operation':"create",
                    'contact': serialized_contact
                }
            )

        # Handle statuses
        for status_data in value.get('statuses', []):
            try:
                message = WAMessage.objects.get(message_id=status_data['id'])
                Status.objects.create(
                    message=message,
                    status=status_data['status']
                )
            except WAMessage.DoesNotExist:
                print(f"Message with ID {status_data['id']} not found.")
            except Exception as e:
                print(f"Error processing status: {e}")

    return Response({"status": "success"})

# ----------------------------------------------------------------
# send messages to whatsapp api
# ----------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Send a message to a contact via WhatsApp API",
    request_body=SendMessageSerializer,
    responses={
        200: openapi.Response(description="Message sent successfully"),
        400: openapi.Response(description="Bad request"),
        500: openapi.Response(description="Error from WhatsApp API")
    }
)
@api_view(['POST'])
def send_to_whatsapp_api(request,contact_id):
    url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Extracting the message data from the request
    message = request.data
    message['to'] = Contact.objects.get(id=contact_id).wa_id
    print(message)

    # Constructing the payload based on the message type
    data = {
        "messaging_product": "whatsapp",
        "to": message.get('to'),
        "type": message.get('message_type', 'text'),
    }

    if message.get('message_type') == 'text':
        data["text"] = {
            "body": message.get('body', '')
        }
    elif message.get('message_type') == 'image':
        data["image"] = {
            "link": message.get('link'),
            "caption": message.get('caption', '')
        }
    elif message.get('message_type') == 'document':
        data["document"] = {
            "link": message.get('link'),
            "caption": message.get('caption', '') 
        }
    print(data)

    # Sending the POST request to WhatsApp API
    try:
        response = requests.post(url, headers=headers, json=data)
        # Return the response from WhatsApp API to the client
        if response.status_code == 200 or response.status_code == 201:
            try:
                message_id = response.json().get('messages', [{}])[0].get('id')
                contact_id = Contact.objects.get(id=contact_id)
                # Convert the ISO string to a datetime object
                timestamp_str = message.get('timestamp')
                if timestamp_str:
                    timestamp_str = timestamp_str.replace('Z', '+00:00')
                    timestamp = datetime.fromisoformat(timestamp_str)
                else:
                    timestamp = None
                sentmessage = WAMessage.objects.create(
                    message_id=message_id,
                    contact=contact_id,
                    message_type=message.get('message_type'),
                    body=message.get('body', ''),
                    link=message.get('link', ''),
                    status='sent',
                    message_mode=message.get('message_mode'),
                    timestamp=timestamp
                )
                serialized_message = WAMessageSerializer(sentmessage).data
                return Response(serialized_message, status=status.HTTP_200_OK)
            except Exception as e:
                print(str(e))
                return Response(status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ----------------------------------------------------------------
# send whatsapp template messages to users
# ----------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Send a template message via WhatsApp API",
    request_body=TemplateMessageSerializer,
    responses={
        200: openapi.Response(description="Template message sent successfully"),
        400: openapi.Response(description="Bad request"),
        500: openapi.Response(description="Error from WhatsApp API")
    }
)
@api_view(['POST'])
def send_whatsapp_message(request):
    details = request.data
    to = details.get('to_phone_number', '') # The phone number you want to send the message to
    template_name = details.get('template_name', '') # The template you want to use
    template_name = template_name.replace(' ', '_').lower()
    language_code = details.get('language_code', 'en_US') # The language code of the template
    url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return Response({'status': 'success', 'message': 'Message sent successfully!'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': response.json()}, status=status.HTTP_400_BAD_REQUEST)