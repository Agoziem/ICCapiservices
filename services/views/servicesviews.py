from re import sub
from ..models import *
from ..serializers import PaginatedServiceSerializer, ServiceSerializer, CategorySerializer, SubCategorySerializer, CreateServiceSerializer, UpdateServiceSerializer
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field,parse_json_fields,get_full_image_url
import json
from django.db.models import Count
from django.http import QueryDict
from collections import Counter
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from ICCapp.models import Organization
from drf_yasg import openapi

User = get_user_model()


# --------------------------------------------------------------------------
# get all services
# --------------------------------------------------------------------------
class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@swagger_auto_schema(
    method='get',
    operation_description="Get all services for a specific organization, with optional category filtering",
    manual_parameters=[
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter services by category name. Use 'All' to fetch all categories.",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: PaginatedServiceSerializer,
        404: "Not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_services(request, organization_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)
        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                services = Service.objects.filter(organization=organization_id, category=service_category).order_by('-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            services = Service.objects.filter(organization=organization_id).order_by('-updated_at')
        
        paginator = ServicePagination()
        result_page = paginator.paginate_queryset(services, request)
        serializer = ServiceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': 'Failed to retrieve services'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@swagger_auto_schema(
    method='get',
    operation_description="Get trending services for a specific organization, sorted by number of buyers",
    manual_parameters=[
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter services by category name. Use 'All' to fetch all categories.",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: PaginatedServiceSerializer,
        404: "Not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_trendingservices(request, organization_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)

        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                services = Service.objects.filter(
                    organization=organization_id, category=service_category
                ).annotate(
                    buyers_count=Count('userIDs_that_bought_this_service')
                ).filter(
                    buyers_count__gt=0  # Exclude services with no buyers
                ).order_by('-buyers_count', '-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            services = Service.objects.filter(
                organization=organization_id
            ).annotate(
                buyers_count=Count('userIDs_that_bought_this_service')
            ).filter(
                buyers_count__gt=0  # Exclude services with no buyers
            ).order_by('-buyers_count', '-updated_at')

        paginator = ServicePagination()
        result_page = paginator.paginate_queryset(services, request)
        serializer = ServiceSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({'error': 'Failed to retrieve trending services'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Get services purchased by a specific user in an organization",
    manual_parameters=[
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter services by category name. Use 'All' to fetch all categories.",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        200: PaginatedServiceSerializer,
        404: "Not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_user_services(request, organization_id, user_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate user exists
        if not User.objects.filter(id=user_id).exists():
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)
        # Query services where the user exists in userIDs_that_bought_this_service (ManyToManyField)
        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                services = Service.objects.filter(
                    organization=organization_id,
                    category=service_category,
                    userIDs_that_bought_this_service__id=user_id
                ).order_by('-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            services = Service.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_service__id=user_id
            ).order_by('-updated_at')

        paginator = ServicePagination()
        result_page = paginator.paginate_queryset(services, request)
        serializer = ServiceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({'error': 'Failed to retrieve user services'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
# --------------------------------------------------------------------------
# get a single service
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific service by ID",
    responses={
        200: ServiceSerializer,
        404: "Service not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# --------------------------------------------------------------------------
# get a service by token
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific service by token",
    responses={
        200: ServiceSerializer,
        404: "Service not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_service_token(request, servicetoken):
    try:
        service = Service.objects.get(service_token=servicetoken)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Add a service view
# --------------------------------------------------------------------------  
@swagger_auto_schema(
    method='post',
    operation_description="Add a new service to an organization",
    request_body=CreateServiceSerializer,
    responses={
        201: ServiceSerializer,
        400: "Bad request"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_service(request, organization_id):
    # Use a mutable version of request.data (without deepcopy)
    if isinstance(request.data, QueryDict):
        data = request.data.copy()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Normalize the file fields
        image_fields = ['preview']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = parse_json_fields(data)
        
        # Add organization to parsed fields
        parsed_json_fields['organization'] = organization_id

        # serialize the field
        serializer = CreateServiceSerializer(data=parsed_json_fields)
        serializer.is_valid(raise_exception=True)
    
        # Retrieve the category object
        category_data = parsed_json_fields['category']
        category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
        category = Category.objects.get(id=category_id)

        # Handle subcategory field if it exist and its not empty (optional fields)
        subcategory = None
        if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
            subcategory_data = parsed_json_fields['subcategory']
            subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
            subcategory = SubCategory.objects.get(id=subcategory_id)

        new_service = serializer.save(
            organization=organization,
            category=category, 
            subcategory=subcategory
            )
        return Response(ServiceSerializer(new_service).data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Failed to create service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Update a service view 
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing service",
    request_body=UpdateServiceSerializer,
    responses={
        200: ServiceSerializer,
        400: "Bad request",
        404: "Service not found"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, service_id):
    
    if isinstance(request.data, QueryDict):
        data = request.data.copy()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    
    try:
        service = Service.objects.get(id=service_id)

        # Normalize the file fields
        image_fields = ['preview']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = parse_json_fields(data)

        # Validate organization if provided
        if 'organization' in parsed_json_fields:
            if not Organization.objects.filter(id=parsed_json_fields['organization']).exists():
                return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        # serialize the field
        serializer = UpdateServiceSerializer(service, data=parsed_json_fields, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update organization if provided
        if 'organization' in parsed_json_fields:
            organization = Organization.objects.get(id=parsed_json_fields['organization'])
            service.organization = organization
        
        # Update category field
        if 'category' in parsed_json_fields and parsed_json_fields['category']:
            category_data = parsed_json_fields['category']
            category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    service.category = category
                except Category.DoesNotExist:
                    return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Update subcategory field (optional fields)
        if 'subcategory' in parsed_json_fields:
            if parsed_json_fields['subcategory']:
                subcategory_data = parsed_json_fields['subcategory']
                subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
                if subcategory_id:
                    try:
                        subcategory = SubCategory.objects.get(id=subcategory_id)
                        service.subcategory = subcategory
                    except SubCategory.DoesNotExist:
                        return Response({'error': 'Subcategory not found'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                service.subcategory = None

        updated_service = serializer.save()
        return Response(ServiceSerializer(updated_service).data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------------------------------------------------------------  
# Delete a service view
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a service",
    responses={
        204: "No Content - Service successfully deleted",
        404: "Service not found"
    }
)
@api_view(['DELETE'])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return Response({'message': 'Service deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to delete service'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
