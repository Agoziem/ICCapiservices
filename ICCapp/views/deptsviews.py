from django.shortcuts import render
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..serializers import *
from utils import normalize_img_field, parse_json_fields
import json
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema

class DepartmentPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow page size to be set via URL query parameter
    max_page_size = 1000  # Max allowed page size

# get all depts by an Organization
@swagger_auto_schema(
    method="get",
    responses={
        200: DepartmentSerializer(many=True),
        404: 'Departments Not Found'
    }
)
@api_view(['GET'])
def get_org_depts(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        departments = Department.objects.filter(organization=organization_id).order_by('id')
        
        if not departments.exists():
            return Response({'error': 'No departments found for this organization'}, status=status.HTTP_404_NOT_FOUND)
            
        paginator = DepartmentPagination()
        # Paginate the queryset
        result_page = paginator.paginate_queryset(departments, request)
        # Serialize the paginated result
        serializer = DepartmentSerializer(result_page, many=True)
        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching departments: {str(e)}")
        return Response({'error': 'An error occurred while fetching departments'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# add a dept
@swagger_auto_schema(
    method="post",
    request_body=CreateDepartmentSerializer,
    responses={
        201: DepartmentSerializer,
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_dept(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Process form data
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
            
        # Normalize and parse data
        data = normalize_img_field(data, "img")
        parsed_data = parse_json_fields(data)
        
        # Validate input data using CreateDepartmentSerializer
        create_serializer = CreateDepartmentSerializer(data=parsed_data)
        if not create_serializer.is_valid():
            return Response(create_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Create department with validated data
        serializer = DepartmentSerializer(data=parsed_data)
        if serializer.is_valid():
            department = serializer.save(organization=organization)
            
            # Set staff in charge if provided
            if parsed_data.get('staff_in_charge'):
                try:
                    staff_in_charge = Staff.objects.get(id=parsed_data.get('staff_in_charge'))
                    department.staff_in_charge = staff_in_charge
                except Staff.DoesNotExist:
                    return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Parse and add services
            services_list = parsed_data.get('services', [])
            for service_name in services_list:
                if service_name:
                    service, created = DepartmentService.objects.get_or_create(name=service_name)
                    department.services.add(service)
            
            department.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating department: {str(e)}")
        return Response({'error': 'An error occurred during department creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# update a dept
@swagger_auto_schema(
    method="put",
    request_body=UpdateDepartmentSerializer,
    responses={
        201: DepartmentSerializer,
        400: 'Bad Request',
        404: 'Department Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_dept(request, department_id):
    try:
        department = Department.objects.get(id=department_id)
        
        # Process form data
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
            
        # Normalize and parse data
        data = normalize_img_field(data, "img")
        parsed_data = parse_json_fields(data)
        
        # Validate input data using UpdateDepartmentSerializer
        update_serializer = UpdateDepartmentSerializer(data=parsed_data)
        if not update_serializer.is_valid():
            return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Update department with validated data
        serializer = DepartmentSerializer(department, data=parsed_data)
        if serializer.is_valid():
            department = serializer.save()

            # Set staff in charge if provided
            if data.get('staff_in_charge'):
                try:
                    staff_in_charge = Staff.objects.get(id=parsed_data.get('staff_in_charge'))
                    department.staff_in_charge = staff_in_charge
                except Staff.DoesNotExist:
                    return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)

            # Parse and update services
            services_list = parsed_data.get('services', [])
            department.services.clear()
            for service_name in services_list:
                if service_name:
                    service, created = DepartmentService.objects.get_or_create(name=service_name)
                    department.services.add(service)
            department.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating department: {str(e)}")
        return Response({'error': 'An error occurred during department update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# delete a dept
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Department deleted successfully',
        404: 'Department Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(['DELETE'])
def delete_dept(request, department_id):
    try:
        department = Department.objects.get(id=department_id)
        department.delete()
        return Response({'message': 'Department deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Department.DoesNotExist:
        return Response({'error': 'Department not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting department: {str(e)}")
        return Response({'error': 'An error occurred during department deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)