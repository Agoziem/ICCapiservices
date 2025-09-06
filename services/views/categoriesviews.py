from ..models import *
from ..serializers import CategorySerializer, CreateCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

# get all categories
@swagger_auto_schema(
    method="get",
    responses={
        200: CategorySerializer(many=True),
        404: 'Categories Not Found'
    }
)
@api_view(['GET'])
def get_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Failed to retrieve categories'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# add a category
@swagger_auto_schema(
    method="post",
    request_body=CreateCategorySerializer,
    responses={
        201: CategorySerializer(),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def add_category(request):
    # Validate input data using serializer
    serializer = CreateCategorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        category_name = serializer.validated_data['category']
        
        # Check if category already exists
        if Category.objects.filter(category=category_name).exists():
            return Response({'error': 'Category already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        category = Category.objects.create(category=category_name)
        response_serializer = CategorySerializer(category, many=False)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': 'Failed to create category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# update a category
@swagger_auto_schema(
    method="put",
    request_body=CreateCategorySerializer,
    responses={
        200: CategorySerializer(),
        400: 'Bad Request',
        404: 'Category Not Found'
    }
)
@api_view(['PUT'])
def update_category(request, category_id):
    # Validate input data using serializer
    serializer = CreateCategorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        category = Category.objects.get(id=category_id)
        category_name = serializer.validated_data['category']
        
        # Check if another category with the same name exists (excluding current)
        if Category.objects.filter(category=category_name).exclude(id=category_id).exists():
            return Response({'error': 'Category name already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        category.category = category_name
        category.save()
        response_serializer = CategorySerializer(category, many=False)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# delete a category
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Category Not Found',
        400: 'Bad Request'
    }
)
@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to delete category'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)