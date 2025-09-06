from ..models import Category
from ..serializers import CategorySerializer, CreateCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema

# get all categories
@swagger_auto_schema(
    method='get',
    operation_description="Get all video categories",
    responses={
        200: CategorySerializer(many=True),
        500: "Internal server error"
    }
)
@api_view(['GET'])
def get_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_categories: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# add a category
@swagger_auto_schema(
    method='post',
    operation_description="Create a new video category",
    request_body=CreateCategorySerializer,
    responses={
        201: CategorySerializer,
        400: "Bad request"
    }
)
@api_view(['POST'])
def add_category(request):
    try:
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate using serializer
        serializer = CreateCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category name
        category_name = serializer.validated_data.get('category')
        if not category_name or not category_name.strip():
            return Response({'error': 'Category name is required and cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate category name
        if Category.objects.filter(category__iexact=category_name.strip()).exists():
            return Response({'error': 'Category with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        category = Category.objects.create(category=category_name.strip())
        response_serializer = CategorySerializer(category, many=False)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in add_category: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# update a category
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing video category",
    request_body=CreateCategorySerializer,
    responses={
        200: CategorySerializer,
        404: "Category not found",
        400: "Bad request"
    }
)
@api_view(['PUT'])
def update_category(request, category_id):
    try:
        # Validate category_id
        if not category_id or not str(category_id).isdigit():
            return Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate using serializer
        serializer = CreateCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category name
        category_name = serializer.validated_data.get('category')
        if not category_name or not category_name.strip():
            return Response({'error': 'Category name is required and cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate category name (excluding current category)
        if Category.objects.filter(category__iexact=category_name.strip()).exclude(id=category_id).exists():
            return Response({'error': 'Category with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        category.category = category_name.strip()
        category.save()
        response_serializer = CategorySerializer(category, many=False)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in update_category: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# delete a category
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a video category",
    responses={
        204: "No Content - Category successfully deleted",
        404: "Category not found",
        400: "Bad request"
    }
)
@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        # Validate category_id
        if not category_id or not str(category_id).isdigit():
            return Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if category has associated subcategories
        if hasattr(category, 'subcategory_set') and category.subcategory_set.exists():
            return Response({'error': 'Cannot delete category with associated subcategories'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if category has associated videos
        if hasattr(category, 'video_set') and category.video_set.exists():
            return Response({'error': 'Cannot delete category with associated videos'}, status=status.HTTP_400_BAD_REQUEST)
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"Error in delete_category: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)