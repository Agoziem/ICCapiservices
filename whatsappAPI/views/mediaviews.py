import requests
from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse





@api_view(['GET'])
def get_media(request, media_id):
    # Step 1: Fetch media metadata from WhatsApp API
    url = f"https://graph.facebook.com/v17.0/{media_id}"
    headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        media = response.json()
        media_url = media.get('url')
        mime_type = media.get('mime_type')
        
        return Response({
            'url': media_url,
            'mime_type': mime_type,
        }, status=status.HTTP_200_OK)
        
    
    # Handle error if the media cannot be fetched
    return Response({
        'error': 'Failed to fetch media metadata from WhatsApp API',
    }, status=status.HTTP_400_BAD_REQUEST)
