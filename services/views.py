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
    print(data)
    try:
        organization = Organization.objects.get(id=organization_id)
        try:
            data = normalize_img_field(data,"preview")
            category = Category.objects.get(category=data.get('category', None))
            service = Service.objects.create(
                organization=organization,
                name=data.get('name', ''),
                description=data.get('description', ''),
                category=category,
                price=data.get('price', 0.0),
            )
            if data.get('preview'):
                service.preview = data.get('preview')
            service.save()
            serializer = ServiceSerializer(service, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
    print(data)
    try:
        service = Service.objects.get(id=service_id)
        try:
            service.name = data.get('name', service.name)
            service.description = data.get('description', service.description)
            category = Category.objects.get(category=data.get('category', service.category))
            service.category = category
            service.price = data.get('price', service.price)
            if data.get('preview'):
                service.preview = data.get('preview')
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
    
# get all categories
@api_view(['GET'])
def get_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# add a category
@api_view(['POST'])
def add_category(request):
    data = request.data.copy()
    try:
        category = Category.objects.create(
            category=data.get('category', None)
        )
        serializer = CategorySerializer(category, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

# update a category
@api_view(['PUT'])
def update_category(request, category_id):
    data = request.data.copy()
    try:
        category = Category.objects.get(id=category_id)
        category.category = data.get('category', category.category)
        category.save()
        serializer = CategorySerializer(category, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# delete a category
@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)