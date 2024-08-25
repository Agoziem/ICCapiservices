from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import *
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateparse import parse_datetime
from django.conf import settings
import requests
from rest_framework import status
from ..serializers import *

# Handle incoming WhatsApp webhook events
@api_view(['POST'])
def whatsapp_webhook(request):
    payload = request.data

    # Store the entire payload for reference
    event_id = payload.get('entry', [{}])[0].get('id')
    WebhookEvent.objects.create(event_id=event_id, payload=payload)

    # Extract and store message data
    entry = payload.get('entry', [])[0]
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
            sentmessage = ReceivedMessage.objects.create(
                message_id=message_data['id'],
                contact=contact,
                message_type=message_data['type'],
                content=message_data.get('text', {}).get('body', ''),
                media_id=message_data.get(message_data['type'], {}).get('id', ''),
                mime_type=message_data.get(message_data['type'], {}).get('mime_type', ''),
                timestamp=parse_datetime(message_data.get('timestamp'))
            )
            serialized_message = RecievedMessageSerializer(sentmessage).data
            # Send the message to the appropriate WebSocket room
            room_name = f'whatsappapi_{contact.wa_id}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat_message',
                    'message': serialized_message
                }
            )
            print(serialized_message)

    # Handle statuses
    for status_data in value.get('statuses', []):
        message = ReceivedMessage.objects.get(message_id=status_data['id'])
        Status.objects.create(
            message=message,
            status=status_data['status'],
            timestamp=parse_datetime(status_data['timestamp'])
        )

    return Response({"status": "success"})

# ----------------------------------------------------------------
# send messages to whatsapp api
# ----------------------------------------------------------------
@api_view(['POST'])
def send_to_whatsapp_api(request):
    url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Extracting the message data from the request
    message = request.data

    # Constructing the payload based on the message type
    data = {
        "messaging_product": "whatsapp",
        "to": message.get('to'),
        "type": message.get('type', 'text'),
    }

    if message.get('type') == 'text':
        data["text"] = {
            "body": message.get('body', '')
        }
    elif message.get('type') == 'image':
        data["image"] = {
            "link": message.get('link'),
            "caption": message.get('caption', '')
        }
    elif message.get('type') == 'document':
        data["document"] = {
            "link": message.get('link'),
            "filename": message.get('filename', '')
        }

    # Sending the POST request to WhatsApp API
    try:
        response = requests.post(url, headers=headers, json=data)

        # Return the response from WhatsApp API to the client
        if response.status_code == 200 or response.status_code == 201:
            message_id = response.json().get('messages', [{}])[0].get('id')
            contact = Contact.objects.get(wa_id=message.get('to'))
            sentmessage = SentMessage.objects.create(
                message_id=message_id,
                contact=contact,
                message_type=message.get('type'),
                body=message.get('body', ''),
                link=message.get('link', ''),
                status='sent'
            )
            serialized_message = SentMessageSerializer(sentmessage).data
            print(serialized_message)
            return Response(serialized_message, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    except requests.exceptions.RequestException as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ----------------------------------------------------------------
# send whatsapp template messages to users
# ----------------------------------------------------------------
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