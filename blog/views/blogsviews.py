import json
from typing import cast
from django.http import QueryDict
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ValidationError
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from utils import normalize_img_field,parse_json_fields
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# get all blogs by an Organization
@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description="Category name filter", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: PaginatedBlogSerializer,
        400: 'Bad Request',
        404: 'Organization or Category Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_org_blogs(request, organization_id):
    try:
        # Validate organization_id
        if not organization_id or not str(organization_id).isdigit():
            return Response({'error': 'Invalid organization ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)
        
        if category and category != "All":
            # Validate category exists
            try:
                blog_category = Category.objects.get(category=category)
                blogs = Blog.objects.filter(organization=organization_id, category=blog_category).order_by('-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            blogs = Blog.objects.filter(organization=organization_id).order_by('-updated_at')
        
        paginator = BlogPagination()
        result_page = paginator.paginate_queryset(blogs, request)
        serializer = BlogSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error retrieving organization blogs: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get all blogs by a User
@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: PaginatedBlogSerializer,
        400: 'Bad Request',
        404: 'User Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_blogs(request, user_id):
    try:
        # Validate user_id
        if not user_id or not str(user_id).isdigit():
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        blogs = Blog.objects.filter(author=user_id).order_by('-updated_at')
        paginator = BlogPagination()
        result_page = paginator.paginate_queryset(blogs, request)
        serializer = BlogSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
        
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error retrieving user blogs: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# get a single blog
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer,
        400: 'Bad Request',
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_blog(request, blog_id):
    try:
        # Validate blog_id
        if not blog_id or not str(blog_id).isdigit():
            return Response({'error': 'Invalid blog ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        blog = Blog.objects.get(id=blog_id)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error retrieving blog: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# get a single blog by slug
@swagger_auto_schema(
    method="get",
    responses={
        200: BlogSerializer,
        400: 'Bad Request',
        404: 'Blog Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_blog_by_slug(request, slug):
    try:
        # Validate slug
        if not slug or not slug.strip():
            return Response({'error': 'Invalid slug'}, status=status.HTTP_400_BAD_REQUEST)
        
        blog = Blog.objects.get(slug=slug)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error retrieving blog by slug: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    method="post",
    request_body=CreateBlogSerializer,
    responses={
        201: BlogSerializer,
        400: 'Bad Request',
        404: 'User, Category, or Organization Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_blog(request, organization_id, user_id):
    """
    Create a blog post for a given organization and author (user).
    Validates request data, slug uniqueness, organization, user, category, and tags.
    """

    try:
        # ✅ Ensure IDs are valid integers
        if not str(organization_id).isdigit() or not str(user_id).isdigit():
            return Response({"error": "Invalid organization or user ID"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Ensure body exists
        if not request.data:
            return Response({"error": "Request body is required"}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy() if isinstance(request.data, QueryDict) else request.data
        normalized_data = normalize_img_field(data, "img")
        parsed_json = parse_json_fields(normalized_data)

        # Remove fields that need special handling
        removed_tags = parsed_json.pop("tags", [])
        
        serializer = CreateBlogSerializer(data=parsed_json)
        serializer.is_valid(raise_exception=True)

        # Ensure org & author exist
        organization = get_object_or_404(Organization, id=organization_id)
        author = get_object_or_404(User, id=user_id)

        # Category (optional)
        category = None
        if parsed_json.get("category"):
            category = get_object_or_404(Category, id=parsed_json["category"])

        # Slug uniqueness
        slug = parsed_json.get("slug")
        if slug and Blog.objects.filter(slug=slug).exists():
            return Response(
                {"error": "Blog with this slug already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save blog with explicit FK assignments
        new_blog = serializer.save(
            organization=organization,
            author=author,
            category=category,
            slug=slug if slug else None,
        )

        # Tags (create if not exist)
        if removed_tags:
            tags = [
                Tag.objects.get_or_create(tag=tag.strip())[0]
                for tag in removed_tags
                if tag and tag.strip()
            ]
            new_blog.tags.set(tags) # type: ignore

        return Response(BlogSerializer(new_blog).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error during blog creation: {str(e)}")
        return Response({"error": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    method="put",
    request_body=UpdateBlogSerializer,
    responses={
        200: BlogSerializer,
        400: 'Bad Request',
        404: 'Blog, User, or Category Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    data = request.data.copy()
    data = normalize_img_field(data, "img")
    parsed_json = parse_json_fields(data)

    removed_category = parsed_json.pop("category", None)
    removed_tags = parsed_json.pop("tags", None)
    removed_author = parsed_json.pop("author", None)
    removed_slug = parsed_json.pop("slug", None)
    serializer = UpdateBlogSerializer(blog, data=parsed_json, partial=True)
    serializer.is_valid(raise_exception=True)

    # Validate & assign related fields
    if removed_category is not None:
        category = Category.objects.filter(id=removed_category).first()
        if not category:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        blog.category = category

    if removed_author is not None:
        author = CustomUser.objects.filter(id=removed_author).first()
        if not author:
            return Response({"error": "Author not found"}, status=status.HTTP_404_NOT_FOUND)
        blog.author = author

    if removed_slug is not None:
        if Blog.objects.exclude(id=blog_id).filter(slug=removed_slug).exists():
            return Response({"error": "Slug already exists"}, status=status.HTTP_400_BAD_REQUEST)
        blog.slug = removed_slug  # 🔑 explicitly assign slug if passed

    # Save basic fields via serializer (title, content, img, etc.)
    updated_blog = serializer.save()

    # Handle tags after saving
    if removed_tags is not None:
        blog.tags.clear()
        tags = removed_tags
        tag_objs = [Tag.objects.get_or_create(tag=tag_name)[0] for tag_name in tags]
        updated_blog.tags.set(tag_objs) # type: ignore

    return Response(BlogSerializer(updated_blog).data, status=status.HTTP_200_OK)



    
# delete a Blog view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        400: 'Bad Request',
        404: 'Blog Not Found'
    }
)
@api_view(['DELETE'])
def delete_blog(request, blog_id):
    try:
        # Validate blog_id
        if not blog_id or not str(blog_id).isdigit():
            return Response({'error': 'Invalid blog ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        return Response({'message': 'Blog deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error during blog deletion: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
@permission_classes([])
def add_views(request, blog_id):
    try:
        # Validate blog_id
        if not blog_id or not str(blog_id).isdigit():
            return Response({'error': 'Invalid blog ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        blog = Blog.objects.get(id=blog_id)
        blog.views += 1
        blog.save()
        return Response({'message': 'View count updated successfully'}, status=status.HTTP_200_OK)
        
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error during view count update: {str(e)}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    







