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
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

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
    data = request.data.copy()
    try:
        category = Category.objects.create(
            category=data.get('category', None)
        )
        serializer = CategorySerializer(category, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

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
    data = request.data.copy()
    try:
        category = Category.objects.get(id=category_id)
        category.category = data.get('category', category.category)
        category.save()
        serializer = CategorySerializer(category, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
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
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)