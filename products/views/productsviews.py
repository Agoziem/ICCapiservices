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
from drf_yasg.utils import swagger_auto_schema
from ICCapp.models import Organization
from django.contrib.auth import get_user_model

User = get_user_model()

# --------------------------------------------------------------------------
# get all products view
# --------------------------------------------------------------------------
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedProductSerializer,
        404: 'Product Not Found'
    }
)
@api_view(['GET'])
def get_products(request, organization_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)
        if category and category != "All":
            try:
                product_category = Category.objects.get(category=category)
                products = Product.objects.filter(organization=organization_id, category=product_category).order_by('-last_updated_date')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = Product.objects.filter(organization=organization_id).order_by('-last_updated_date')
        
        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        return Response({'error': 'Failed to retrieve products'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedProductSerializer,
        404: 'Product Not Found'
    }
)
@api_view(['GET'])
def get_trendingproducts(request, organization_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)

        if category and category != "All":
            try:
                product_category = Category.objects.get(category=category)
                products = Product.objects.filter(
                    organization=organization_id, category=product_category
                ).annotate(
                    buyers_count=Count('userIDs_that_bought_this_product')
                ).filter(
                    buyers_count__gt=0  # Exclude products with no buyers
                ).order_by('-buyers_count', '-last_updated_date')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
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

    except Exception as e:
        return Response({'error': 'Failed to retrieve trending products'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedProductSerializer,
        404: 'Product Not Found'
    }
)
@api_view(['GET'])
def get_user_products(request, organization_id, user_id):
    try:
        # Validate organization exists
        if not Organization.objects.filter(id=organization_id).exists():
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate user exists
        if not User.objects.filter(id=user_id).exists():
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)

        # Filter products based on category and user purchase (ManyToManyField)
        if category and category != "All":
            try:
                product_category = Category.objects.get(category=category)
                products = Product.objects.filter(
                    organization=organization_id,
                    category=product_category,
                    userIDs_that_bought_this_product__id=user_id
                ).order_by('-last_updated_date')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            products = Product.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_product__id=user_id
            ).order_by('-last_updated_date')

        paginator = ProductPagination()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
        return Response({'error': 'Failed to retrieve user products'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------------------------------------------------------------   
# get a single product view
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="get",
    responses={
        200: ProductSerializer,
        404: 'Product Not Found'
    }
)
@api_view(['GET'])
def get_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------   
# Add a Product view
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="post",
    request_body=CreateProductSerializer,
    responses={
        201: ProductSerializer,
        400: 'Bad Request',
        404: 'Category Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_product(request, organization_id):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Normalize image fields
        image_fields = ['preview', 'product']
        for field in image_fields:
            data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the QueryDict
        parsed_json_fields = parse_json_fields(data)
        
        # Add organization to parsed fields
        parsed_json_fields['organization'] = organization_id

        # Validate required fields
        if 'name' not in parsed_json_fields or not parsed_json_fields['name']:
            return Response({'error': 'Product name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'description' not in parsed_json_fields or not parsed_json_fields['description']:
            return Response({'error': 'Product description is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'price' not in parsed_json_fields or not parsed_json_fields['price']:
            return Response({'error': 'Product price is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'category' not in parsed_json_fields or not parsed_json_fields['category']:
            return Response({'error': 'Product category is required'}, status=status.HTTP_400_BAD_REQUEST)
    
        serializer = ProductSerializer(data=parsed_json_fields)

        if serializer.is_valid():
            product = serializer.save()

            # Set the organization
            product.organization = organization
            
            # Retrieve the category object
            category_data = parsed_json_fields['category']
            category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
            category = Category.objects.get(id=category_id)
            product.category = category
            
            # Handle subcategory field if it exist and its not empty (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                subcategory_data = parsed_json_fields['subcategory']
                subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
                subcategory = SubCategory.objects.get(id=subcategory_id)
                product.subcategory = subcategory

            # Save the product with the relational fields
            product.save()

            return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Failed to create product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


# --------------------------------------------------------------------------
# update a Product view
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="put",
    request_body=UpdateProductSerializer,
    responses={
        200: ProductSerializer,
        400: 'Bad Request',
        404: 'Product or Category Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_product(request, product_id):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()  # Convert QueryDict to a mutable dictionary
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

        # Validate organization if provided
        if 'organization' in parsed_json_fields:
            if not Organization.objects.filter(id=parsed_json_fields['organization']).exists():
                return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update product fields
        serializer = ProductSerializer(product, data=parsed_json_fields, partial=True)

        if serializer.is_valid():
            product = serializer.save()
            
            # Update organization if provided
            if 'organization' in parsed_json_fields:
                organization = Organization.objects.get(id=parsed_json_fields['organization'])
                product.organization = organization

            # Update category field
            if 'category' in parsed_json_fields and parsed_json_fields['category']:
                category_data = parsed_json_fields['category']
                category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                        product.category = category
                    except Category.DoesNotExist:
                        return Response({'error': 'Category not found'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Update subcategory field (optional fields)
            if 'subcategory' in parsed_json_fields:
                if parsed_json_fields['subcategory']:
                    subcategory_data = parsed_json_fields['subcategory']
                    subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
                    if subcategory_id:
                        try:
                            subcategory = SubCategory.objects.get(id=subcategory_id)
                            product.subcategory = subcategory
                        except SubCategory.DoesNotExist:
                            return Response({'error': 'Subcategory not found'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    product.subcategory = None
                    
            product.save()
            return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------------------------------------------------------------------
# delete a Product view
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Product Not Found'
    }
)
@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to delete product'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)