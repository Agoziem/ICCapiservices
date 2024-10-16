from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
import json
from django.db.models import Count

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
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)

        # Normalize image fields
        image_fields = ['preview', 'product']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = {}
        for field in data:
            if field not in image_fields:
                try:
                    parsed_json_fields[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # If field is not JSON, keep it as is
                    parsed_json_fields[field] = data[field]

        # Retrieve the category object
        category = Category.objects.get(id=parsed_json_fields['category'].get('id'))

        # Create the product
        product = Product.objects.create(
            organization=organization,
            name=parsed_json_fields.get('name', ''),
            description=parsed_json_fields.get('description', ''),
            category=category,
            price=parsed_json_fields.get('price', 0.0),
            digital=parsed_json_fields.get('digital', False),
            free=parsed_json_fields.get('free', False),
        )

         # Handle subcategory field if it exist and its not empty (optional fields)
        if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
            subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
            product.subcategory = subcategory

        # Handle image & file fields
        for field in image_fields:
            if data.get(field):
                setattr(product, field, data.get(field))

        product.save()
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST) 


# --------------------------------------------------------------------------
# update a Product view
# --------------------------------------------------------------------------
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    data = request.data.copy()
    try:
        product = Product.objects.get(id=product_id)

        # Normalize image fields
        image_fields = ['preview','product']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Parse JSON fields
        for field in data:
            if field not in image_fields:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # If field is not JSON, keep it as is
                    pass

        # Update product fields
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.digital = data.get('digital', product.digital)
        product.free = data.get('free', product.free)

        # Update category field
        if 'category' in data:
            try:
                category_id = data['category'].get('id')
                if category_id:
                    category = Category.objects.get(id=category_id)
                    product.category = category
            except Category.DoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update subcategory field (optional fields)
        if 'subcategory' in data and data['subcategory']:
                subcategory_id = data['subcategory'].get('id')
                if subcategory_id:
                    subcategory = SubCategory.objects.get(id=subcategory_id)
                    product.subcategory = subcategory
        else:
            product.subcategory = None

        # Handle image fields
        for field in image_fields:
            if field in data:
                setattr(product, field, data.get(field, getattr(product, field)))

        product.save()
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
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