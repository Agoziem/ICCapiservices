import requests
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def fetch_media_from_whatsapp_api(media_url):
    """Helper function to fetch media from WhatsApp API"""
    try:
        if not media_url or not media_url.strip():
            return None
        
        headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
        response = requests.get(media_url, headers=headers, stream=True, timeout=30)
        
        if response.status_code == 200:
            return response
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching media from WhatsApp API: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in fetch_media_from_whatsapp_api: {e}")
        return None


@swagger_auto_schema(
    method='get',
    operation_description="Fetch and stream media content from WhatsApp API using media ID",
    responses={
        200: openapi.Response(description="Media content streamed successfully"),
        404: openapi.Response(description="Media URL not found or invalid"),
        400: openapi.Response(description="Bad request"),
        500: openapi.Response(description="Internal server error")
    }
)
@api_view(['GET'])
def get_media(request, media_id):
    try:
        # Validate media_id
        if not media_id or not media_id.strip():
            return Response({'error': 'Invalid media ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate WhatsApp access token configuration
        if not hasattr(settings, 'WHATSAPP_ACCESS_TOKEN') or not settings.WHATSAPP_ACCESS_TOKEN:
            return Response({'error': 'WhatsApp access token not configured'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Step 1: Fetch media metadata from WhatsApp API
        url = f"https://graph.facebook.com/v17.0/{media_id.strip()}"
        headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching media metadata: {e}")
            return Response({'error': 'Failed to connect to WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if response.status_code == 200:
            try:
                media = response.json()
                media_url = media.get('url')
                mime_type = media.get('mime_type')
                
                if not media_url:
                    return Response({'error': 'Media URL not found in response'}, status=status.HTTP_404_NOT_FOUND)
                
                # Step 2: Fetch the actual media content
                media_response = fetch_media_from_whatsapp_api(media_url)
                
                if media_response:
                    # Stream the media content directly
                    return StreamingHttpResponse(
                        media_response.iter_content(chunk_size=8192),
                        content_type=mime_type or 'application/octet-stream'
                    )
                else:
                    return Response({'error': 'Failed to fetch media content'}, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                print(f"Error parsing JSON response: {e}")
                return Response({'error': 'Invalid response from WhatsApp API'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif response.status_code == 404:
            return Response({'error': 'Media not found'}, status=status.HTTP_404_NOT_FOUND)
        elif response.status_code == 401:
            return Response({'error': 'Unauthorized access to WhatsApp API'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'error': f'WhatsApp API error: {response.status_code}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in get_media: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
