from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser
from datetime import datetime
from .models import WhatsAppBusinessAccount, Contact, Message



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


# webhook to recieve whatsapp messages
@csrf_exempt
@api_view(['POST'])
def whatsapp_webhook(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            # Extract and save data
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    
                    # WhatsAppBusinessAccount
                    account_id = entry.get('id')
                    display_phone_number = value.get('metadata', {}).get('display_phone_number')
                    phone_number_id = value.get('metadata', {}).get('phone_number_id')
                    whatsapp_account, created = WhatsAppBusinessAccount.objects.get_or_create(
                        account_id=account_id,
                        defaults={'display_phone_number': display_phone_number, 'phone_number_id': phone_number_id}
                    )

                    # Contact
                    for contact in value.get('contacts', []):
                        wa_id = contact.get('wa_id')
                        profile_name = contact.get('profile', {}).get('name')
                        contact_obj, created = Contact.objects.get_or_create(
                            wa_id=wa_id,
                            defaults={'profile_name': profile_name}
                        )

                        # Message
                        for message in value.get('messages', []):
                            message_id = message.get('id')
                            timestamp = datetime.fromtimestamp(int(message.get('timestamp')))
                            text_body = message.get('text', {}).get('body', '')
                            message_type = message.get('type', 'text')
                            Message.objects.create(
                                whatsapp_account=whatsapp_account,
                                contact=contact_obj,
                                message_id=message_id,
                                timestamp=timestamp,
                                text_body=text_body,
                                message_type=message_type
                            )

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print("Error processing webhook:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        

# api view to reply messages
@api_view(['POST'])
def reply_message(request):
    details = request.data
    to = details.get('to_phone_number', '')
    body = details.get('text', '')
    type = details.get('type', 'text')
    url = f"https://graph.facebook.com/{settings.WHATSAPP_VERSION}/{settings.WHATSAPP_FROM_PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": type,
        "text": {
            "body": body
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return Response({'status': 'success', 'message': 'Message sent successfully!'}, status=status.HTTP_200_OK)
    else:
        return Response({'status': 'error', 'message': response.json()}, status=status.HTTP_400_BAD_REQUEST)

