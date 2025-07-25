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
    method="get",
    responses={
        200: SubCategorySerializer(),
        404: 'Subcategory Not Found'
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
        category = Category.objects.get(id=data['category'].get('id'))
        subcategory = SubCategory.objects.create(subcategory=data['subcategory'],category=category)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
    method="delete",
    responses={
        204: 'No Content',
        404: 'Subcategory Not Found'
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
        