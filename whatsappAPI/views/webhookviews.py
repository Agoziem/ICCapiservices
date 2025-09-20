from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ValidationError
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
from ..serializers import WebhookPayloadSerializer, SendMessageSerializer, TemplateMessageSerializer




@swagger_auto_schema(
    method='post',
    operation_description="Webhook for receiving WhatsApp messages and statuses from Meta's WhatsApp Business API",
    request_body=WebhookPayloadSerializer,
    responses={
        200: openapi.Response(description="Success"),
        400: "Bad request",
        500: "Internal server error"
    }
)
@api_view(['POST'])
def whatsapp_webhook(request):
    try:
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        payload = request.data

        # Validate required webhook structure
        entry = payload.get('entry', [])
        if not entry:
            return Response({'error': 'Invalid webhook payload: missing entry'}, status=status.HTTP_400_BAD_REQUEST)
        
        entry = entry[0] if isinstance(entry, list) else entry
        event_id = entry.get('id')
        
        if not event_id:
            return Response({'error': 'Invalid webhook payload: missing event ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Store the entire payload for reference
        WebhookEvent.objects.get_or_create(event_id=event_id, defaults={'payload': payload})
        
        # Start a database transaction
        with transaction.atomic():
            changes = entry.get('changes', [])
            if not changes:
                return Response({"status": "success", "message": "No changes to process"})
            
            changes = changes[0] if isinstance(changes, list) else changes
            value = changes.get('value', {})

            # Handle contacts
            for contact_data in value.get('contacts', []):
                try:
                    # Validate contact data
                    wa_id = contact_data.get('wa_id')
                    if not wa_id:
                        print("Missing wa_id in contact data")
                        continue
                    
                    profile_name = contact_data.get('profile', {}).get('name', '') if contact_data.get('profile') else ''
                    
                    contact, created = Contact.objects.get_or_create(
                        wa_id=wa_id,
                        defaults={'profile_name': profile_name}
                    )
                    
                    # Handle messages
                    for message_data in value.get('messages', []):
                        try:
                            # Validate message data
                            message_id = message_data.get('id')
                            message_type = message_data.get('type')
                            
                            if not message_id or not message_type:
                                print(f"Missing required message fields: id={message_id}, type={message_type}")
                                continue
                            
                            # Extract message content based on type
                            body = ''
                            media_id = ''
                            mime_type = ''
                            caption = ''
                            filename = ''
                            
                            if message_type == 'text':
                                body = message_data.get('text', {}).get('body', '')
                            else:
                                # For media messages
                                media_content = message_data.get(message_type, {})
                                media_id = media_content.get('id', '')
                                mime_type = media_content.get('mime_type', '')
                                caption = media_content.get('caption', '')
                                filename = media_content.get('filename', '')
                            
                            # Check if message already exists
                            if WAMessage.objects.filter(message_id=message_id).exists():
                                print(f"Message {message_id} already exists, skipping")
                                continue
                            
                            recieved_message = WAMessage.objects.create(
                                message_id=message_id,
                                contact=contact,
                                message_type=message_type,
                                body=body,
                                media_id=media_id,
                                mime_type=mime_type,
                                caption=caption,
                                filename=filename,
                            )
                            serialized_message = WAMessageSerializer(recieved_message).data

                            # Send the message to the appropriate WebSocket room
                            try:
                                room_name = f'whatsappapi_messages'
                                channel_layer = get_channel_layer()
                                if channel_layer:
                                    async_to_sync(channel_layer.group_send)(
                                        room_name,
                                        {
                                            'type': 'chat_message',
                                            'operation': "create",
                                            'contact': ContactSerializer(contact).data,
                                            'message': serialized_message
                                        }
                                    )
                            except Exception as ws_error:
                                print(f"WebSocket error: {ws_error}")
                                # Continue processing even if WebSocket fails
                                
                        except Exception as e:
                            print(f"Error processing message: {e}")
                            continue

                    # Serialize the contact for WebSocket broadcast
                    try:
                        serialized_contact = ContactSerializer(contact).data
                        general_room_name = 'whatsappapi_contacts'
                        channel_layer = get_channel_layer()
                        if channel_layer:
                            async_to_sync(channel_layer.group_send)(
                                general_room_name,
                                {
                                    'type': 'chat_message',
                                    'operation': "create",
                                    'contact': serialized_contact
                                }
                            )
                    except Exception as ws_error:
                        print(f"WebSocket error for contacts: {ws_error}")
                        # Continue processing
                        
                except Exception as e:
                    print(f"Error processing contact: {e}")
                    continue
            # Handle statuses
            for status_data in value.get('statuses', []):
                try:
                    # Validate status data
                    message_id = status_data.get('id')
                    status_value = status_data.get('status')
                    
                    if not message_id or not status_value:
                        print(f"Missing required status fields: id={message_id}, status={status_value}")
                        continue
                    
                    try:
                        message = WAMessage.objects.get(message_id=message_id)
                        Status.objects.create(
                            message=message,
                            status=status_value
                        )
                    except WAMessage.DoesNotExist:
                        print(f"Message with ID {message_id} not found.")
                        continue
                        
                except Exception as e:
                    print(f"Error processing status: {e}")
                    continue

        return Response({"status": "success"})
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in whatsapp_webhook: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ----------------------------------------------------------------
# send messages to whatsapp api
# ----------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Send a message to a contact via WhatsApp API",
    request_body=SendMessageSerializer,
    responses={
        200: openapi.Response(description="Message sent successfully"),
        404: "Contact not found",
        400: "Bad request",
        500: "Error from WhatsApp API"
    }
)
@api_view(['POST'])
def send_to_whatsapp_api(request, contact_id):
    try:
        # Validate contact_id
        if not contact_id or not str(contact_id).isdigit():
            return Response({'error': 'Invalid contact ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate contact exists
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate using serializer
        serializer = SendMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate WhatsApp configuration
        required_settings = ['WHATSAPP_VERSION', 'WHATSAPP_FROM_PHONE_NUMBER_ID', 'WHATSAPP_ACCESS_TOKEN']
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                return Response({'error': f'WhatsApp configuration missing: {setting}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Extracting the message data from the request
        message = request.data
        message['to'] = contact.wa_id
        print(message)

        # Validate message type and required fields
        message_type = message.get('message_type', 'text')
        
        # Constructing the payload based on the message type
        data = {
            "messaging_product": "whatsapp",
            "to": message.get('to'),
            "type": message_type,
        }

        if message_type == 'text':
            body = message.get('body', '').strip()
            if not body:
                return Response({'error': 'Message body is required for text messages'}, status=status.HTTP_400_BAD_REQUEST)
            data["text"] = {"body": body}
        elif message_type == 'image':
            link = message.get('link', '').strip()
            if not link:
                return Response({'error': 'Link is required for image messages'}, status=status.HTTP_400_BAD_REQUEST)
            data["image"] = {
                "link": link,
                "caption": message.get('caption', '')
            }
        elif message_type == 'document':
            link = message.get('link', '').strip()
            if not link:
                return Response({'error': 'Link is required for document messages'}, status=status.HTTP_400_BAD_REQUEST)
            data["document"] = {
                "link": link,
                "caption": message.get('caption', '') 
            }
        else:
            return Response({'error': f'Unsupported message type: {message_type}'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(data)

        # Sending the POST request to WhatsApp API
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            # Return the response from WhatsApp API to the client
            if response.status_code in [200, 201]:
                try:
                    response_data = response.json()
                    message_id = response_data.get('messages', [{}])[0].get('id')
                    
                    if not message_id:
                        return Response({'error': 'No message ID returned from WhatsApp API'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Convert the ISO string to a datetime object
                    timestamp_str = message.get('timestamp')
                    timestamp = None
                    if timestamp_str:
                        try:
                            timestamp_str = timestamp_str.replace('Z', '+00:00')
                            timestamp = datetime.fromisoformat(timestamp_str)
                        except ValueError as e:
                            print(f"Error parsing timestamp: {e}")
                    
                    sentmessage = WAMessage.objects.create(
                        message_id=message_id,
                        contact=contact,
                        message_type=message_type,
                        body=message.get('body', ''),
                        link=message.get('link', ''),
                        status='sent',
                        message_mode=message.get('message_mode', ''),
                        timestamp=timestamp
                    )
                    serialized_message = WAMessageSerializer(sentmessage).data
                    return Response(serialized_message, status=status.HTTP_200_OK)
                except (ValueError, KeyError) as e:
                    print(f"Error processing WhatsApp API response: {e}")
                    return Response({'error': 'Invalid response from WhatsApp API'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                error_message = f"WhatsApp API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message += f" - {error_data}"
                except:
                    pass
                return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)

        except requests.exceptions.Timeout:
            return Response({'error': 'Request timeout to WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return Response({'error': 'Failed to connect to WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in send_to_whatsapp_api: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ----------------------------------------------------------------
# send whatsapp template messages to users
# ----------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Send a template message via WhatsApp API",
    request_body=TemplateMessageSerializer,
    responses={
        200: openapi.Response(description="Template message sent successfully"),
        400: "Bad request",
        500: "Error from WhatsApp API"
    }
)
@api_view(['POST'])
def send_whatsapp_message(request):
    try:
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate using serializer
        serializer = TemplateMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract data from request
        details = request.data
        to_phone_number = details.get('to_phone_number', '').strip() if details.get('to_phone_number') else ''
        template_name = details.get('template_name', '').strip() if details.get('template_name') else ''
        language_code = details.get('language_code', 'en_US')
        
        # Validate required fields
        if not to_phone_number:
            return Response({'error': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not template_name:
            return Response({'error': 'Template name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate WhatsApp configuration
        required_settings = ['WHATSAPP_VERSION', 'WHATSAPP_FROM_PHONE_NUMBER_ID', 'WHATSAPP_ACCESS_TOKEN']
        for setting in required_settings:
            if not hasattr(settings, setting) or not getattr(settings, setting):
                return Response({'error': f'WhatsApp configuration missing: {setting}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Format template name
        template_name = template_name.replace(' ', '_').lower()
        
        url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
        headers = {
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }

        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                return Response({
                    'status': 'success', 
                    'message': 'Template message sent successfully!'
                }, status=status.HTTP_200_OK)
            else:
                error_message = f"WhatsApp API error: {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', error_message)
                except:
                    pass
                return Response({
                    'status': 'error', 
                    'message': error_message
                }, status=status.HTTP_400_BAD_REQUEST)
        except requests.exceptions.Timeout:
            return Response({'error': 'Request timeout to WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return Response({'error': 'Failed to connect to WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in send_whatsapp_message: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)