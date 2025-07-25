from ..models import Category, SubCategory
from ..serializers import SubCategorySerializer, CreateSubCategorySerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


# get all subcategories
@swagger_auto_schema(
    method='get',
    operation_description="Get all subcategories for a specific video category",
    responses={
        200: SubCategorySerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_subcategories(request,category_id):
    try:
        category = Category.objects.get(id=category_id)
        subcategories = SubCategory.objects.filter(category=category)
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get subcategory by id
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video subcategory by ID",
    responses={
        200: SubCategorySerializer,
        404: "Subcategory not found"
    }
)
@api_view(['GET'])
def get_subcategory(request,subcategory_id):
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# create a new subcategory
@swagger_auto_schema(
    method='post',
    operation_description="Create a new video subcategory",
    request_body=CreateSubCategorySerializer,
    responses={
        201: SubCategorySerializer,
        404: "Category not found"
    }
)
@api_view(['POST'])
def create_subcategory(request):
    data = request.data
    print(data)
    try:
        category = Category.objects.get(id=data['category'].get('id'))
        subcategory = SubCategory.objects.create(subcategory=data['subcategory'],category=category)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a subcategory
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing video subcategory",
    request_body=CreateSubCategorySerializer,
    responses={
        200: SubCategorySerializer,
        404: "Subcategory not found"
    }
)
@api_view(['PUT'])
def update_subcategory(request,subcategory_id):
    data = request.data
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        subcategory.subcategory = data['subcategory']
        category = Category.objects.get(id=data['category'].get('id'))
        subcategory.category = category
        subcategory.save()
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# delete a subcategory
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a video subcategory",
    responses={
        204: "No Content - Subcategory successfully deleted",
        404: "Subcategory not found"
    }
)
@api_view(['DELETE'])
def delete_subcategory(request,subcategory_id):
    try:
        subcategory = SubCategory.objects.get(id=subcategory_id)
        subcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except SubCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
        