from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

# get all categories
@swagger_auto_schema(method="get", responses={200: CategorySerializer(many=True), 404: 'Categories Not Found'})
@api_view(['GET'])
def get_categories(request):
    try:
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({'error': 'Categories not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching categories: {str(e)}")
        return Response({'error': 'An error occurred while fetching categories'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# add a category
@swagger_auto_schema(method="post", request_body=CreateCategorySerializer, responses={201: CategorySerializer, 400: 'Bad Request'})
@api_view(['POST'])
def add_category(request):
    # Validate input data using serializer
    serializer = CreateCategorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        category = Category.objects.create(
            category=validated_data.get('category')
        )
        category_serializer = CategorySerializer(category, many=False)
        return Response(category_serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error creating category: {str(e)}")
        return Response({'error': 'An error occurred during category creation'}, status=status.HTTP_400_BAD_REQUEST)
    

# update a category
@swagger_auto_schema(method="put", request_body=CreateCategorySerializer, responses={200: CategorySerializer, 404: 'Category Not Found', 400: 'Bad Request'})
@api_view(['PUT'])
def update_category(request, category_id):
    # Validate input data using serializer
    serializer = CreateCategorySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        category = Category.objects.get(id=category_id)
        category.category = validated_data.get('category', category.category)
        category.save()
        category_serializer = CategorySerializer(category, many=False)
        return Response(category_serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating category: {str(e)}")
        return Response({'error': 'An error occurred during category update'}, status=status.HTTP_400_BAD_REQUEST)

# delete a category
@swagger_auto_schema(method="delete", responses={204: 'No Content', 404: 'Category Not Found', 400: 'Bad Request'})
@api_view(['DELETE'])
def delete_category(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        return Response({'message': 'Category deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting category: {str(e)}")
        return Response({'error': 'An error occurred during category deletion'}, status=status.HTTP_400_BAD_REQUEST)