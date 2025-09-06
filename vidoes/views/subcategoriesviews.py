from ..models import Category, SubCategory
from ..serializers import SubCategorySerializer, CreateSubCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema


# get all subcategories
@swagger_auto_schema(
    method='get',
    operation_description="Get all subcategories for a specific video category",
    responses={
        200: SubCategorySerializer(many=True),
        404: "Category not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
def get_subcategories(request, category_id):
    try:
        # Validate category_id
        if not category_id or not str(category_id).isdigit():
            return Response({'error': 'Invalid category ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_subcategories: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get subcategory by id
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video subcategory by ID",
    responses={
        200: SubCategorySerializer,
        404: "Subcategory not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
def get_subcategory(request, subcategory_id):
    try:
        # Validate subcategory_id
        if not subcategory_id or not str(subcategory_id).isdigit():
            return Response({'error': 'Invalid subcategory ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate subcategory exists
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_subcategory: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# create a new subcategory
@swagger_auto_schema(
    method='post',
    operation_description="Create a new video subcategory",
    request_body=CreateSubCategorySerializer,
    responses={
        201: SubCategorySerializer,
        404: "Category not found",
        400: "Bad request"
    }
)
@api_view(['POST'])
def create_subcategory(request):
    try:
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        
        # Validate subcategory name
        subcategory_name = data.get('subcategory')
        if not subcategory_name or not subcategory_name.strip():
            return Response({'error': 'Subcategory name is required and cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category data
        category_data = data.get('category')
        if not category_data:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check for duplicate subcategory name within the same category
        if SubCategory.objects.filter(subcategory__iexact=subcategory_name.strip(), category=category).exists():
            return Response({'error': 'Subcategory with this name already exists in this category'}, status=status.HTTP_400_BAD_REQUEST)
        
        subcategory = SubCategory.objects.create(
            subcategory=subcategory_name.strip(),
            category=category
        )
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in create_subcategory: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update a subcategory
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing video subcategory",
    request_body=CreateSubCategorySerializer,
    responses={
        200: SubCategorySerializer,
        404: "Subcategory not found",
        400: "Bad request"
    }
)
@api_view(['PUT'])
def update_subcategory(request, subcategory_id):
    try:
        # Validate subcategory_id
        if not subcategory_id or not str(subcategory_id).isdigit():
            return Response({'error': 'Invalid subcategory ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        
        # Validate subcategory exists
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate subcategory name
        subcategory_name = data.get('subcategory')
        if not subcategory_name or not subcategory_name.strip():
            return Response({'error': 'Subcategory name is required and cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category data
        category_data = data.get('category')
        if not category_data:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate category exists
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check for duplicate subcategory name within the same category (excluding current subcategory)
        if SubCategory.objects.filter(
            subcategory__iexact=subcategory_name.strip(), 
            category=category
        ).exclude(id=subcategory_id).exists():
            return Response({'error': 'Subcategory with this name already exists in this category'}, status=status.HTTP_400_BAD_REQUEST)
        
        subcategory.subcategory = subcategory_name.strip()
        subcategory.category = category
        subcategory.save()
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in update_subcategory: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# delete a subcategory
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a video subcategory",
    responses={
        204: "No Content - Subcategory successfully deleted",
        404: "Subcategory not found",
        400: "Bad request"
    }
)
@api_view(['DELETE'])
def delete_subcategory(request, subcategory_id):
    try:
        # Validate subcategory_id
        if not subcategory_id or not str(subcategory_id).isdigit():
            return Response({'error': 'Invalid subcategory ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate subcategory exists
        try:
            subcategory = SubCategory.objects.get(id=subcategory_id)
        except SubCategory.DoesNotExist:
            return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
        subcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"Error in delete_subcategory: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        