from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import WebhookEvent, Contact, Message, Status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.dateparse import parse_datetime
from django.conf import settings
import requests
from rest_framework import status

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
            message = Message.objects.create(
                message_id=message_data['id'],
                contact=contact,
                message_type=message_data['type'],
                content=message_data.get('text', {}).get('body', ''),
                media_id=message_data.get(message_data['type'], {}).get('id', ''),
                mime_type=message_data.get(message_data['type'], {}).get('mime_type', ''),
                timestamp=parse_datetime(message_data.get('timestamp'))
            )

            # Send the message to the appropriate WebSocket room
            room_name = f'whatsappapi_{contact.wa_id}'
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                room_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'wa_id': contact.wa_id,
                        'body': message.content,
                        'timestamp': message.timestamp.isoformat(),
                        'message_id': message.message_id,
                        'type': message.message_type,
                        'media_id': message.media_id,
                        'mime_type': message.mime_type,
                    }
                }
            )

    # Handle statuses
    for status_data in value.get('statuses', []):
        message = Message.objects.get(message_id=status_data['id'])
        Status.objects.create(
            message=message,
            status=status_data['status'],
            timestamp=parse_datetime(status_data['timestamp'])
        )

    return Response({"status": "success"})

# send whatsapp template messages
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