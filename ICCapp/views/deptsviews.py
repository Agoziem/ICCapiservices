from django.shortcuts import render
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..serializers import *
from utils import normalize_img_field
import json
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict
from rest_framework.parsers import MultiPartParser, FormParser

class DepartmentPagination(PageNumberPagination):
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow page size to be set via URL query parameter
    max_page_size = 1000  # Max allowed page size

# get all depts by an Organization
@api_view(['GET'])
def get_org_depts(request, organization_id):
    try:
        departments = Department.objects.filter(organization=organization_id).order_by('id')  # Add ordering if necessary
        paginator = DepartmentPagination()
        # Paginate the queryset
        result_page = paginator.paginate_queryset(departments, request)
        # Serialize the paginated result
        serializer = DepartmentSerializer(result_page, many=True)
        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
    except Department.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# add a dept
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_dept(request,organization_id):    
    try:
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        data = normalize_img_field(data,"img")
        parsed_data = parse_json_fields(data)
        organization = Organization.objects.get(id=organization_id)
        serializer = DepartmentSerializer(data=parsed_data)
        if serializer.is_valid():
            department = serializer.save(organization=organization)
            if parsed_data.get('staff_in_charge'):
                staff_in_charge = Staff.objects.get(id=parsed_data.get('staff_in_charge'))
                department.staff_in_charge = staff_in_charge
            # Parse the services JSON string into a list of dictionaries
            services_list = parsed_data.get('services', [])
            for service_name in services_list:
                if service_name:
                    service, created = DepartmentService.objects.get_or_create(name=service_name)
                    department.services.add(service)
            department.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response({'error': 'Error in adding dept'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# update a dept
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_dept(request, department_id):
    try:
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        department = Department.objects.get(id=department_id)
        data = normalize_img_field(data, "img")
        parsed_data = parse_json_fields(data)
        serializer = DepartmentSerializer(department,data=parsed_data)
        if serializer.is_valid():
            department = serializer.save()

            if data.get('staff_in_charge'):
                staff_in_charge = Staff.objects.get(id=parsed_data.get('staff_in_charge'))
                department.staff_in_charge = staff_in_charge

            # Parse the services JSON string into a list of dictionaries
            services_list = parsed_data.get('services', [])
            department.services.clear()
            for service_name in services_list:
                if service_name:
                    service, created = DepartmentService.objects.get_or_create(name=service_name)
                    department.services.add(service)
            department.save()
            return Response(DepartmentSerializer(department).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Department.DoesNotExist:
        return Response({'error': 'Department does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response({'error': 'Error in updating department'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# delete a dept
@api_view(['DELETE'])
def delete_dept(request,department_id):
    try:
        department = Department.objects.get(id=department_id)
        department.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Department.DoesNotExist:
        return Response({'error': 'Dept does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response({'error': 'Error in deleting dept'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)