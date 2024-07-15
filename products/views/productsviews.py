from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field

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
@parser_classes([MultiPartParser, FormParser])
def add_product(request,organization_id):
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)
        data = normalize_img_field(data,"preview")
        category = Category.objects.get(category=data.get('category', None))
        product = Product.objects.create(
            organization=organization,
            name=data.get('name', ''),
            description=data.get('description', ''),
            category=category,
            price=data.get('price', 0.0),
            digital=data.get('digital', True)
        )
        if data.get('preview'):
            product.preview = data.get('preview')
        product.save()
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

# update a Product view
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    data = request.data.copy()
    try:
        product = Product.objects.get(id=product_id)
        data = normalize_img_field(data,"preview")
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        category = Category.objects.get(category=data.get('category', product.category.category))
        product.category = category
        product.price = data.get('price', product.price)
        if 'preview' in data:
            product.preview = data.get('preview')
        product.save()
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# delete a Product view
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)