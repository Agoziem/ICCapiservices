from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

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
def add_service(request, organization_id):
    try:
        name=request.data.get('name')
        price=request.data.get('price')
        description=request.data.get('description', None)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        service = Service.objects.create(organization=organization_id, name=name, price=price, description=description)
        serializer = ServiceSerializer(service, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# Update a service view
@api_view(['PUT'])
def update_service(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        try:
            service.name = request.data.get('name', service.name)
            service.price = request.data.get('price', service.price)
            service.description = request.data.get('description', service.description)
            service.save()
            serializer = ServiceSerializer(service, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
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