from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field,parse_json_fields
import json
from django.db.models import Count
from django.http import QueryDict

# --------------------------------------------------------------------------
# get all services
# --------------------------------------------------------------------------
class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

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


@api_view(['POST'])
def add_user_to_in_progress(request, service_id, user_id):
    """
    Add the given user_id to the 'userIDs_whose_services_is_in_progress' field.
    """
    try:
        service = Service.objects.get(id=service_id)

        if user_id not in service.userIDs_whose_services_is_in_progress:
            service.userIDs_whose_services_is_in_progress.append(user_id)
            service.save()
            return Response(
                {"message": f"User {user_id} added to in-progress services."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": f"User {user_id} already in in-progress services."},
                status=status.HTTP_200_OK
            )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
def add_user_to_completed(request, service_id, user_id):
    """
    Add the given user_id to the 'userIDs_whose_services_have_been_completed' field.
    """
    try:
        service = Service.objects.get(id=service_id)

        if user_id not in service.userIDs_whose_services_have_been_completed:
            service.userIDs_whose_services_have_been_completed.append(user_id)
            service.save()
            return Response(
                {"message": f"User {user_id} added to completed services."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": f"User {user_id} already in completed services."},
                status=status.HTTP_200_OK
            )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
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
# get a service by token
# --------------------------------------------------------------------------
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
@api_view(['DELETE'])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
