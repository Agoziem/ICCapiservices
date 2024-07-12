from django.shortcuts import render
import requests
from django.conf import settings
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from rest_framework.parsers import JSONParser


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
@api_view(['GET', 'POST'])
def whatsapp_webhook(request):
    if request.method == 'GET':
        VERIFY_TOKEN = settings.WHATSAPP_WEBHOOK_TOKEN

        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode and token:
            if mode == 'subscribe' and token == VERIFY_TOKEN:
                return HttpResponse(challenge, status=200)
            else:
                return HttpResponse(status=403)
        return HttpResponse(status=400)

    elif request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            # Handle the webhook payload
            print("Webhook received:", data)

            # Process the data (e.g., save to database, trigger some action, etc.)

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print("Error processing webhook:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
# api view to reply messages