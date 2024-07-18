from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
import json

# --------------------------------------------------------------------------
# get all services
# --------------------------------------------------------------------------
@api_view(['GET'])
def get_services(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        services = Service.objects.filter(organization=organization).order_by('-updated_at')
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------------------------------
# get a single service
# --------------------------------------------------------------------------
@api_view(['GET'])
def get_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------------------------------
# Add a service view
# --------------------------------------------------------------------------  
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_service(request, organization_id):
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)

        image_fields = ['preview']
        # Normalize image fields
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = {}
        for field in data:
            if field not in image_fields:
                try:
                    parsed_json_fields[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # If field is not JSON, keep it as is
                    parsed_json_fields[field] = data[field]

        # Retrieve the category object
        category = Category.objects.get(id=parsed_json_fields['category'].get('id'))

        # Create the service
        service = Service.objects.create(
            organization=organization,
            name=parsed_json_fields.get('name', ''),
            description=parsed_json_fields.get('description', ''),
            category=category,
            price=parsed_json_fields.get('price', 0.0),
            service_flow=parsed_json_fields.get('service_flow', ''),
        )

        # Handle subcategory field if it exist and its not empty (optional fields)
        if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
            subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
            service.subcategory = subcategory


        # Handle image fields
        for field in image_fields:
            if data.get(field):
                setattr(service, field, data.get(field))

        service.save()
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Category.DoesNotExist:
        return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response({"detail": "Organization not found."}, status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------------------------------
# Update a service view
# --------------------------------------------------------------------------
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, service_id):
    data = request.data.copy()
    try:
        service = Service.objects.get(id=service_id)

        # Normalize image fields
        image_fields = ['preview']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Parse JSON fields
        for field in data:
            if field not in image_fields:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # If field is not JSON, keep it as is
                    pass

        # Update service fields
        service.name = data.get('name', service.name)
        service.description = data.get('description', service.description)
        service.price = data.get('price', service.price)
        service.service_flow = data.get('service_flow', service.service_flow)

        # Update category field
        if 'category' in data:
            try:
                category_id = data['category'].get('id')
                if category_id:
                    category = Category.objects.get(id=category_id)
                    service.category = category
            except Category.DoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Update subcategory field (optional fields)
        if 'subcategory' in data and data['subcategory']:
                subcategory_id = data['subcategory'].get('id')
                if subcategory_id:
                    subcategory = SubCategory.objects.get(id=subcategory_id)
                    service.subcategory = subcategory
        else:
            service.subcategory = None

        # Handle image fields
        for field in image_fields:
            if field in data:
                setattr(service, field, data.get(field))

        service.save()
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------------------------------------------  
# Delete a service view
# --------------------------------------------------------------------------
@api_view(['DELETE'])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
