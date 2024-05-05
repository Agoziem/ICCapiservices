from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# get all products view
@api_view(['GET'])
def get_products(request,organization_id):
    try:
        products = Product.objects.filter(organization=organization_id)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single product view
@api_view(['GET'])
def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a Product view
@api_view(['POST'])
def add_product(request,organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# update a Product view
@api_view(['PUT'])
def update_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a Product view
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)