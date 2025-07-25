import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def fetch_media_from_whatsapp_api(media_url):
    headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
    response = requests.get(media_url, headers=headers, stream=True)
    if response.status_code == 200:
        # Stream the binary content of the media
        return response
    return None


@swagger_auto_schema(
    method='get',
    operation_description="Fetch and stream media content from WhatsApp API using media ID",
    responses={
        200: openapi.Response(description="Media content streamed successfully"),
        404: openapi.Response(description="Media URL not found or invalid"),
        400: openapi.Response(description="Failed to fetch media metadata from WhatsApp API")
    }
)
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
        
        if media_url:
            # Step 2: Fetch the actual media content
            media_response = fetch_media_from_whatsapp_api(media_url)
            
            if media_response:
                # Stream the media content directly
                return StreamingHttpResponse(
                    media_response.iter_content(chunk_size=8192),
                    content_type=mime_type
                )
        
        return Response({
            'error': 'Media URL not found or invalid',
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Handle error if the media cannot be fetched
    return Response({
        'error': 'Failed to fetch media metadata from WhatsApp API',
    }, status=status.HTTP_400_BAD_REQUEST)
