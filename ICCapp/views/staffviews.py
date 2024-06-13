from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status

# get all staff
@api_view(['GET'])
def get_staffs(request, organization_id):
    try:
        staffs = Staff.objects.filter(organization=organization_id)
        serializer = StaffSerializer(staffs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
        data = request.data.copy()
        if data.get('img') == '':
            data['img'] = None
        serializer = StaffSerializer(data=data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a staff view
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        data = request.data.copy()
        if data.get('img') == '':
            data['img'] = None
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