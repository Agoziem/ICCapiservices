import json
from typing import cast
from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from utils import normalize_img_field,parse_json_fields
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# get all blogs by an Organization
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer(many=True),
        404: 'Not Found'
    }
)
@api_view(['GET'])
def get_org_blogs(request,organization_id):
    try:
        category = request.GET.get('category', None)
        if category and category != "All":
            blog_category = Category.objects.get(category=category)
            blogs = Blog.objects.filter(organization=organization_id, category=blog_category).order_by('-updated_at')
        else:
            blogs = Blog.objects.filter(organization=organization_id).order_by('-updated_at')
        paginator = BlogPagination()
        result_page = paginator.paginate_queryset(blogs, request)
        serializer = BlogSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get all blogs by a User
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer(many=True),
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
def get_blogs(request,user_id):
    try:
        blogs = Blog.objects.filter(author=user_id).order_by('-updated_at')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get a single blog
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer,
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
def get_blog(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single blog by slug
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer,
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
def get_blog_by_slug(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



@swagger_auto_schema(
    method="post",
    request_body=CreateBlogSerializer,
    responses={
        201: BlogSerializer,
        400: 'Bad Request',
        404: 'User or Category Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_blog(request, organization_id, user_id):
    # Validate input data using serializer
    serializer = CreateBlogSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse and normalize image field
        data = request.data.copy()
        normalized_data = normalize_img_field(data, "img")
        parsed_json = parse_json_fields(normalized_data)
        
        # Validate the parsed data again with the serializer
        blog_serializer = BlogSerializer(data=parsed_json)

        if blog_serializer.is_valid():
            # Save the blog instance without relational fields
            blog = blog_serializer.save()

            # Set relational fields manually
            blog.author = User.objects.get(id=parsed_json.get("author"))
            blog.category = Category.objects.get(id=parsed_json.get("category"))

            # Handle tags: create missing tags and set them
            tag_objects = [Tag.objects.get_or_create(tag=name.strip())[0] for name in parsed_json.get("tags", [])]
            blog.tags.set(tag_objects)

            # Save the blog with the relational fields
            blog.save()

            return Response(BlogSerializer(blog).data, status=status.HTTP_201_CREATED)
        return Response(blog_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except (User.DoesNotExist, Category.DoesNotExist) as e:
        return Response({"error": f"Related object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during blog creation: {str(e)}")
        return Response({"error": f"An error occurred during blog creation: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)



@swagger_auto_schema(
    method="put",
    request_body=UpdateBlogSerializer,
    responses={
        200: BlogSerializer,
        400: 'Bad Request',
        404: 'User or Category Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_blog(request, blog_id):
    # Validate input data using serializer
    serializer = UpdateBlogSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Parse and normalize the image field
        data = normalize_img_field(request.data.copy(), "img")
        parsed_json = parse_json_fields(data)

        # Fetch the existing blog instance
        blog = Blog.objects.get(id=blog_id)
        blog_serializer = BlogSerializer(blog, data=parsed_json)

        if blog_serializer.is_valid():
            # Save the blog instance without relational fields
            blog = blog_serializer.save()

            # Set relational fields manually
            blog.author = User.objects.get(id=parsed_json.get("author"))
            blog.category = Category.objects.get(id=parsed_json.get("category"))

            # Handle tags: Create missing tags and set them
            tag_names = parsed_json.get("tags", [])
            tag_objects = [Tag.objects.get_or_create(tag=name.strip())[0] for name in tag_names]
            blog.tags.set(tag_objects)
            blog.save()

            return Response(BlogSerializer(blog).data, status=status.HTTP_200_OK)
        print(f"Blog serializer errors: {blog_serializer.errors}")
        return Response(blog_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Blog.DoesNotExist:
        return Response({"error": "Blog not found"}, status=status.HTTP_404_NOT_FOUND)
    except (User.DoesNotExist, Category.DoesNotExist) as e:
        return Response({"error": f"Related object not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during blog update: {str(e)}")
        return Response({"error": f"An error occurred during blog update: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


    
# delete a Blog view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Blog Not Found'
    }
)
@api_view(['DELETE'])
def delete_blog(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        return Response({'message': 'Blog deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during blog deletion: {str(e)}")
        return Response({'error': 'An error occurred during blog deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# increase the blog views
@swagger_auto_schema(
    method="get",
    responses={
        200: 'OK',
        400: 'Bad Request',
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
def add_views(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog.views += 1
        blog.save()
        return Response({'message': 'View count updated successfully'}, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during view count update: {str(e)}")
        return Response({'error': 'An error occurred while updating view count'}, status=status.HTTP_400_BAD_REQUEST)
    







