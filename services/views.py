from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

# get all services
@api_view(['GET'])
def get_services(request, organization_id):
    try:
        services = Service.objects.filter(organization=organization_id)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# get a single service
@api_view(['GET'])
def get_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a service view
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_service(request, organization_id):
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)
        try:
            if data.get('preview') == '':
                data['preview'] = None
            serializer = ServiceSerializer(data=data)
            if serializer.is_valid():
                serializer.save(organization=organization)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist: 
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Update a service view
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_service(request, service_id):
    data = request.data.copy()
    try:
        service = Service.objects.get(id=service_id)
        try:
            if data.get('preview') == '':
                data['preview'] = None
            service_serializer = ServiceSerializer(instance=service, data=data)
            if service_serializer.is_valid():
                service_serializer.save()
                return Response(service_serializer.data, status=status.HTTP_200_OK)
            print(service_serializer.errors)
            return Response(service_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Delete a service view
@api_view(['DELETE'])
def delete_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)