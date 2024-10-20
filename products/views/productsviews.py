from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field,parse_json_fields
import json
from django.db.models import Count
from django.http import QueryDict

# --------------------------------------------------------------------------
# get all products view
# --------------------------------------------------------------------------
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(['GET'])
def get_products(request, organization_id):
    try:
        category = request.GET.get('category', None)
        if category and category != "All":
            product_category = Category.objects.get(category=category)
            products = Product.objects.filter(organization=organization_id, category=product_category).order_by('-last_updated_date')
        else:
            products = Product.objects.filter(organization=organization_id).order_by('-last_updated_date')
        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_trendingproducts(request, organization_id):
    try:
        category = request.GET.get('category', None)

        if category and category != "All":
            product_category = Category.objects.get(category=category)
            products = Product.objects.filter(
                organization=organization_id, category=product_category
            ).annotate(
                buyers_count=Count('userIDs_that_bought_this_product')
            ).filter(
                buyers_count__gt=0  # Exclude products with no buyers
            ).order_by('-buyers_count', '-last_updated_date')
        else:
            products = Product.objects.filter(
                organization=organization_id
            ).annotate(
                buyers_count=Count('userIDs_that_bought_this_product')
            ).filter(
                buyers_count__gt=0  # Exclude products with no buyers
            ).order_by('-buyers_count', '-last_updated_date')

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_user_products(request, organization_id, user_id):
    try:
        category = request.GET.get('category', None)

        # Filter products based on category and user purchase (ManyToManyField)
        if category and category != "All":
            product_category = Category.objects.get(category=category)
            products = Product.objects.filter(
                organization=organization_id,
                category=product_category,
                userIDs_that_bought_this_product__id=user_id
            ).order_by('-last_updated_date')
        else:
            products = Product.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_product__id=user_id
            ).order_by('-last_updated_date')

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# --------------------------------------------------------------------------   
# get a single product view
# --------------------------------------------------------------------------
@api_view(['GET'])
def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------------------------------   
# Add a Product view
# --------------------------------------------------------------------------
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_product(request, organization_id):
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        # Normalize image fields
        image_fields = ['preview', 'product']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = parse_json_fields(data)
    
        serializer = ProductSerializer(data=parsed_json_fields)

        if serializer.is_valid():
            product = serializer.save()

            # Retrieve the Organization as well
            product.organization = Organization.objects.get(id=parsed_json_fields['organization'])

            # Retrieve the category object
            product.category = Category.objects.get(id=parsed_json_fields['category'].get('id'))
            
            # Handle subcategory field if it exist and its not empty (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
                product.subcategory = subcategory

            # Save the blog with the relational fields
            product.save()

            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist or Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST) 


# --------------------------------------------------------------------------
# update a Product view
# --------------------------------------------------------------------------
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        product = Product.objects.get(id=product_id)

        # Normalize image and File fields
        image_fields = ['preview','product']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Parse JSON fields
        parsed_json_fields = parse_json_fields(data)

        # Update product fields
        serializer = ProductSerializer(product,data=parsed_json_fields)

        if serializer.is_valid():
            product = serializer.save()
            
            # Retrieve the Organization as well
            product.organization = Organization.objects.get(id=parsed_json_fields['organization'])

            # Update category field
            if 'category' in parsed_json_fields:
                try:
                    category_id = parsed_json_fields['category'].get('id')
                    if category_id:
                        category = Category.objects.get(id=category_id)
                        product.category = category
                except Category.DoesNotExist:
                    return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update subcategory field (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                    subcategory_id = parsed_json_fields['subcategory'].get('id')
                    if subcategory_id:
                        subcategory = SubCategory.objects.get(id=subcategory_id)
                        product.subcategory = subcategory
            else:
                product.subcategory = None
            product.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist or Category.DoesNotExist or Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


# --------------------------------------------------------------------------
# delete a Product view
# --------------------------------------------------------------------------
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)