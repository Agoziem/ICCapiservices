from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from ..models import Contact, WAMessage, WATemplateSchema
from ..serializers import WAMessageSerializer, ContactSerializer, WATemplateSchemaSerializer
from drf_yasg.utils import swagger_auto_schema


@swagger_auto_schema(
    method='get',
    operation_description="Get all WhatsApp messages for a specific contact",
    responses={
        200: WAMessageSerializer(many=True),
        404: "Contact not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
def message_list(request, contact_id):
    try:
        # Validate contact_id
        if not contact_id or not str(contact_id).isdigit():
            return Response({'error': 'Invalid contact ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate contact exists
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
        
        WAmessages = WAMessage.objects.filter(contact_id=contact_id)
        WAmessages_serializer = WAMessageSerializer(WAmessages, many=True)
        return Response(WAmessages_serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in message_list: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="Get all WhatsApp contacts",
    responses={
        200: ContactSerializer(many=True),
        500: "Internal server error"
    }
)
@api_view(['GET'])
def contact_list(request):
    try:
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in contact_list: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View to get all templates and create a new one
@swagger_auto_schema(
    method='get',
    operation_description="Get all WhatsApp templates",
    responses={
        200: WATemplateSchemaSerializer(many=True),
        500: "Internal server error"
    }
)
@swagger_auto_schema(
    method='post',
    operation_description="Create a new WhatsApp template",
    request_body=WATemplateSchemaSerializer,
    responses={
        201: WATemplateSchemaSerializer,
        400: "Bad request"
    }
)
@api_view(['GET', 'POST'])
def template_list_create(request):
    try:
        # GET request: Retrieve all templates
        if request.method == 'GET':
            templates = WATemplateSchema.objects.all()
            serializer = WATemplateSchemaSerializer(templates, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # POST request: Create a new template
        elif request.method == 'POST':
            # Validate input data
            if not request.data:
                return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate using serializer
            serializer = WATemplateSchemaSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check for duplicate template name if applicable
            template_name = serializer.validated_data.get('name')
            if template_name and WATemplateSchema.objects.filter(name__iexact=template_name).exists():
                return Response({'error': 'Template with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in template_list_create: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

