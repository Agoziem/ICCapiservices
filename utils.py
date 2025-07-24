# utils.py
import re
from django.conf import settings
import json
from functools import wraps
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

def get_full_image_url(image_field, base_url=settings.DJANGO_IMAGE_URL):
    if not image_field:
        return None

    # Get the image URL
    image_url = image_field.url
    
    # Fix percent-encoded colons first
    pattern_percent_3A = r'%3A'
    image_url = re.sub(pattern_percent_3A, ':', image_url)

    # Check if the URL is relative and needs to be prefixed with base URL
    if re.match(r'^/?media/(http|https):', image_url):
        image_url = re.sub(r'^/?media/', '', image_url)

    if not image_url.startswith(('http://', 'https://', 'https:', 'http:')):
        image_url = f"{base_url}{image_url}"

    return image_url



def get_image_name(image_field):
    if not image_field:
        return None 
    return image_field.name.split('/')[-1]


def normalize_img_field(data, key):
    """
    If the field is None, 'null', or contains a valid file, leave it as is.
    If the field is an empty string or the string 'null', set it to None.
    """
    value = data.get(key)

    # If the field is an empty string or 'null', set it to None
    if value == "" or value == "null":
        data[key] = None  # Set the value to None

    # Keep the field if it's None or a valid file
    elif value is None or hasattr(value, 'file'):
        return data  # Leave as is

    # Remove the field if it's an invalid string (anything else)
    elif isinstance(value, str):
        data.pop(key, None)  # Safely remove the key if it exists

    return data






def parse_json_fields(data, exclude_fields=None):
    """
    Parse JSON-like fields from a QueryDict and return a dictionary with 
    parsed values. Exclude specific fields like image fields.
    """
    exclude_fields = exclude_fields or []
    parsed_data = {}

    for field, value in data.items():
        if field in exclude_fields:
            parsed_data[field] = value  # Skip parsing image fields
        else:
            try:
                parsed_data[field] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_data[field] = value  # Keep as-is if not JSON

    return parsed_data






def swagger_doc(
    method='get',
    input_schema=None,         # dict or openapi.Schema
    required=None,
    output_schemas=None,       # dict of status_code: (description, schema_dict or openapi.Schema)
    query_params=None,         # list of dicts: [{name, type, required, description}]
):
    def decorator(view_func):
        # --- Build request body ---
        request_body = None
        if isinstance(input_schema, dict):
            request_body = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={k: openapi.Schema(type=v) for k, v in input_schema.items()},
                required=required or []
            )
        elif isinstance(input_schema, openapi.Schema):
            request_body = input_schema

        # --- Build responses ---
        responses = {}
        if output_schemas:
            for status, (desc, schema_data) in output_schemas.items():
                if isinstance(schema_data, dict):
                    schema = openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={k: openapi.Schema(type=v) for k, v in schema_data.items()}
                    )
                elif isinstance(schema_data, openapi.Schema):
                    schema = schema_data
                else:
                    schema = None
                responses[status] = openapi.Response(desc, schema=schema)

        # --- Build query parameters ---
        manual_parameters = []
        if query_params:
            for param in query_params:
                manual_parameters.append(
                    openapi.Parameter(
                        name=param['name'],
                        in_=openapi.IN_QUERY,
                        type=param['type'],
                        required=param.get('required', False),
                        description=param.get('description', '')
                    )
                )

        # --- Final wrapper ---
        decorated = swagger_auto_schema(
            method=method,
            request_body=request_body,
            responses=responses if responses else None,
            manual_parameters=manual_parameters if manual_parameters else None
        )(view_func)

        @wraps(view_func)
        def wrapper(*args, **kwargs):
            return decorated(*args, **kwargs)

        return wrapper
    return decorator
