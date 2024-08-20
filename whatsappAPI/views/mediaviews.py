import requests
from django.conf import settings
from django.http import HttpResponse
from django.core.files.storage import default_storage

def get_media(request, media_id):
    # Try to serve from local storage first
    media_path = f"media/{media_id}"
    if default_storage.exists(media_path):
        with default_storage.open(media_path, 'rb') as f:
            return HttpResponse(f.read(), content_type='application/octet-stream')

    # Fetch from WhatsApp API if not found locally
    url = f"https://graph.facebook.com/v17.0/{media_id}"
    headers = {'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        # Save the file locally
        with default_storage.open(media_path, 'wb') as f:
            f.write(response.content)
        
        return HttpResponse(response.content, content_type=content_type)
    return HttpResponse(status=404)
