from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from utils import normalize_img_field
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict

class StaffPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000 

# get all staff
@api_view(['GET'])
def get_staffs(request, organization_id):
    try:
        staffs = Staff.objects.filter(organization=organization_id).order_by('id')  # Adjust ordering if necessary
        paginator = StaffPagination()
        # Paginate the queryset using the paginator and request object
        result_page = paginator.paginate_queryset(staffs, request)
        # Serialize the paginated data
        serializer = StaffSerializer(result_page, many=True)
        # Return the paginated response with metadata
        return paginator.get_paginated_response(serializer.data)
    except Staff.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

        
# get a single staff
@api_view(['GET'])
def get_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        serializer = StaffSerializer(staff, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Staff.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a staff view
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_staff(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        data = normalize_img_field(data,"img")
        serializer = StaffSerializer(data=data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a staff view
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        data = normalize_img_field(data,"img")
        serializer = StaffSerializer(instance=staff, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Staff.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a staff view
@api_view(['DELETE'])
def delete_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Staff.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)