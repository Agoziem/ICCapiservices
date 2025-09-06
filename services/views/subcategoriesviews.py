from ..models import *
from ..serializers import SubCategorySerializer, CategorySerializer, CreateSubCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


# get all subcategories
@swagger_auto_schema(
    method="get",
    responses={
        200: SubCategorySerializer(many=True),
        404: 'Subcategories Not Found'
    }
)
@api_view(['GET'])
def get_subcategories(request, category_id):
    try:
        category = Category.objects.get(id=category_id)
        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve subcategories'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get subcategory by id
@swagger_auto_schema(
    method="get",
    responses={
        200: SubCategorySerializer(),
        404: 'Subcategory Not Found'
    }
)
@api_view(['GET'])
def get_subcategory(request, subcategory_id):
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve subcategory'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# create a new subcategory
@swagger_auto_schema(
    method="post",
    request_body=CreateSubCategorySerializer,
    responses={
        201: SubCategorySerializer(),
        404: 'Category Not Found'
    }
)
@api_view(['POST'])
def create_subcategory(request):
    data = request.data
    try:
        # Validate required fields
        if 'subcategory' not in data or not data['subcategory']:
            return Response({'error': 'Subcategory name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'category' not in data:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get category ID from the nested data
        category_data = data['category']
        if isinstance(category_data, dict):
            category_id = category_data.get('id')
        else:
            category_id = category_data
        
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        category = Category.objects.get(id=category_id)
        subcategory_name = data['subcategory']
        
        # Check if subcategory already exists for this category
        if SubCategory.objects.filter(subcategory=subcategory_name, category=category).exists():
            return Response({'error': 'Subcategory already exists for this category'}, status=status.HTTP_400_BAD_REQUEST)
        
        subcategory = SubCategory.objects.create(subcategory=subcategory_name, category=category)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to create subcategory'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update a subcategory
@swagger_auto_schema(
    method="put",
    request_body=CreateSubCategorySerializer,
    responses={
        200: SubCategorySerializer(),
        404: 'Subcategory or Category Not Found'
    }
)
@api_view(['PUT'])
def update_subcategory(request, subcategory_id):
    data = request.data
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        
        # Validate required fields
        if 'subcategory' not in data or not data['subcategory']:
            return Response({'error': 'Subcategory name is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'category' not in data:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get category ID from the nested data
        category_data = data['category']
        if isinstance(category_data, dict):
            category_id = category_data.get('id')
        else:
            category_id = category_data
        
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        category = Category.objects.get(id=category_id)
        subcategory_name = data['subcategory']
        
        # Check if another subcategory with the same name exists for this category (excluding current)
        if SubCategory.objects.filter(subcategory=subcategory_name, category=category).exclude(id=subcategory_id).exists():
            return Response({'error': 'Subcategory name already exists for this category'}, status=status.HTTP_400_BAD_REQUEST)
        
        subcategory.subcategory = subcategory_name
        subcategory.category = category
        subcategory.save()
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update subcategory'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# delete a subcategory
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Subcategory Not Found'
    }
)
@api_view(['DELETE'])
def delete_subcategory(request, subcategory_id):
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        subcategory.delete()
        return Response({'message': 'Subcategory deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except SubCategory.DoesNotExist:
        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to delete subcategory'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        