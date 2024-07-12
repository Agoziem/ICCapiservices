from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status

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
@api_view(['POST'])
def whatsapp_webhook(request):
    try:
        body = request.data
        print(body)
        # if "messages" in body["entry"][0]["changes"][0]["value"]:
        #     messages = body["entry"][0]["changes"][0]["value"]["messages"]
        #     for message in messages:
        #         if message["type"] == "text":
        #             from_number = message["from"]
        #             text = message["text"]["body"]
        #             # Process the message and respond
        #             response_text = f"Received your message: {text}"
        #             send_whatsapp_message(from_number, response_text)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# api view to reply messages