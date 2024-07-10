# utils.py
import re
from django.conf import settings

def get_full_image_url(image_field, base_url=settings.DJANGO_IMAGE_URL):
    if not image_field:
        return None

    # Get the image URL
    image_url = image_field.url
    
    # Fix percent-encoded colons first
    pattern_percent_3A = r'%3A'
    image_url = re.sub(pattern_percent_3A, ':', image_url)

    # Check if the URL is relative and needs to be prefixed with base URL
    if not image_url.startswith(('http://', 'https://')):
        image_url = f"{base_url}{image_url}"

    return image_url



def get_image_name(image_field):
    if not image_field:
        return None 
    return image_field.name.split('/')[-1]

def normalize_img_field(data, key):
    if data.get(key) == '':
        data[key] = None
    elif data.get(key) is not None and not hasattr(data.get(key), 'file'):
        data.pop(key)
    return data
