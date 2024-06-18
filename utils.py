# utils.py
import re

def get_full_image_url(image_field, base_url='http://127.0.0.1:8000'):
    if not image_field:
        return None 

    image_url = image_field.url
    if not image_url.startswith(('http://', 'https://')):
        image_url = f"{base_url}{image_url}"

    # Define regex patterns
    pattern_media = r'^/media/'
    pattern_percent_3A = r'%3A'

    # Modify the URL
    modified_url = re.sub(pattern_media, '', image_url)
    modified_url = re.sub(pattern_percent_3A, ':/', modified_url, count=1)
    modified_url = re.sub(pattern_percent_3A, ':', modified_url)

    return modified_url


def get_image_name(image_field):
    if not image_field:
        return None 
    return image_field.name.split('/')[-1]

def normalize_img_field(data,key):
    if data.get(key) == '':
        data[key] = None
    elif data.get(key) is not None and not hasattr(data.get(key), 'file'):
        data.pop(key)
    return data