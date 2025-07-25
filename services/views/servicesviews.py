from ..models import *
from ..serializers import ServiceSerializer, CategorySerializer, SubCategorySerializer, CreateServiceSerializer, UpdateServiceSerializer
from rest_framework.decorators import api_view, parser_classes
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
    responses={
        200: ServiceSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_services(request, organization_id):
    try:
        category = request.GET.get('category', None)
        if category and category != "All":
            service_category = Category.objects.get(category=category)
            services = Service.objects.filter(organization=organization_id, category=service_category).order_by('-updated_at')
        else:
            services = Service.objects.filter(organization=organization_id).order_by('-updated_at')
        paginator = ServicePagination()
        result_page = paginator.paginate_queryset(services, request)
        serializer = ServiceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

@swagger_auto_schema(
    method='get',
    operation_description="Get trending services for a specific organization, sorted by number of buyers",
    responses={
        200: ServiceSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_trendingservices(request, organization_id):
    try:
        category = request.GET.get('category', None)

        if category and category != "All":
            service_category = Category.objects.get(category=category)
            services = Service.objects.filter(
                organization=organization_id, category=service_category
            ).annotate(
                buyers_count=Count('userIDs_that_bought_this_service')
            ).filter(
                buyers_count__gt=0  # Exclude services with no buyers
            ).order_by('-buyers_count', '-updated_at')
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

    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    operation_description="Get services purchased by a specific user in an organization",
    responses={
        200: ServiceSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_user_services(request, organization_id, user_id):
    try:
        category = request.GET.get('category', None)
        # Query services where the user exists in userIDs_that_bought_this_service (ManyToManyField)
        if category and category != "All":
            service_category = Category.objects.get(category=category)
            services = Service.objects.filter(
                organization=organization_id,
                category=service_category,
                userIDs_that_bought_this_service__id=user_id
            ).order_by('-updated_at')
        else:
            services = Service.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_service__id=user_id
            ).order_by('-updated_at')

        paginator = ServicePagination()
        result_page = paginator.paginate_queryset(services, request)
        serializer = ServiceSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    
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
def get_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
def get_service_token(request, servicetoken):
    try:
        service = Service.objects.get(service_token=servicetoken)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

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
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        # Normalize the file fields
        image_fields = ['preview']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = parse_json_fields(data)

        # serialize the field
        serializer = ServiceSerializer(data=parsed_json_fields)
        if serializer.is_valid():
            service = serializer.save()

            # Retrieve the Organization as well
            service.organization = Organization.objects.get(id=parsed_json_fields['organization'])
            # Retrieve the category object
            service.category = Category.objects.get(id=parsed_json_fields['category'].get('id'))

            # Handle subcategory field if it exist and its not empty (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
                service.subcategory = subcategory

            service.save()
            return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Category.DoesNotExist or Organization.DoesNotExist:
        return Response({"detail": "Category or Organization not found."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------------------------------
# Update a service view 
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing service",
    request_body=UpdateServiceSerializer,
    responses={
        201: ServiceSerializer,
        400: "Bad request",
        404: "Service not found"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, service_id):
    
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
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

         # serialize the field
        serializer = ServiceSerializer(service,data=parsed_json_fields)
        if serializer.is_valid():
            service = serializer.save()

            # Retrieve the Organization as well
            service.organization = Organization.objects.get(id=parsed_json_fields['organization'])
            # Update category field
            if 'category' in parsed_json_fields:
                try:
                    category_id = parsed_json_fields['category'].get('id')
                    if category_id:
                        category = Category.objects.get(id=category_id)
                        service.category = category
                except Category.DoesNotExist:
                    return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Update subcategory field (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                    subcategory_id = parsed_json_fields['subcategory'].get('id')
                    if subcategory_id:
                        subcategory = SubCategory.objects.get(id=subcategory_id)
                        service.subcategory = subcategory
            else:
                service.subcategory = None

            service.save()
            return Response(ServiceSerializer(service).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Service.DoesNotExist:
        return Response({"detail": "Service not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
