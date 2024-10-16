from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from utils import normalize_img_field

User = get_user_model()

class BlogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# get all blogs by an Organization
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
@api_view(['GET'])
def get_blogs(request,user_id):
    try:
        blogs = Blog.objects.filter(author=user_id).order_by('-updated_at')
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get a single blog
@api_view(['GET'])
def get_blog(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single blog by slug
@api_view(['GET'])
def get_blog_by_slug(request, slug):
    try:
        blog = Blog.objects.get(slug=slug)
        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def add_blog(request, organization_id, user_id):
    data = request.data.copy()
    try:
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=organization_id)
        data = normalize_img_field(data, "img")
        title = data.get('title', None)
        subtitle = data.get('subtitle', None)
        body = data.get('body', None)
        readTime = data.get('readTime', 0)
        tags = data.get('tags', [])
        tags_list = tags.split(',')
        slug = data.get('slug', None)
        category = data.get('category', None)
        category, created = Category.objects.get_or_create(category=category)

        blog = Blog.objects.create(
            author=user,
            organization=organization,
            title=title,
            subtitle=subtitle,
            body=body,
            slug=slug,
            category=category,
            readTime=readTime
        )
        
        for tag in tags_list:
            tag, created = Tag.objects.get_or_create(tag=tag)
            blog.tags.add(tag)
        
        if data.get("img"):
            img = data.get("img")
            blog.img = img
        blog.save()

        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist or Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def update_blog(request, blog_id):
    data = request.data.copy()
    try:
        blog = Blog.objects.get(id=blog_id)
        data = normalize_img_field(data, "img")
        blog.title = data.get('title', blog.title)
        blog.subtitle = data.get('subtitle', blog.subtitle)
        blog.body = data.get('body', blog.body)
        blog.readTime = data.get('readTime', blog.readTime)
        tags = data.get('tags', [])
        tags_list = tags.split(',')
        blog.slug = data.get('slug', blog.slug)
        category = data.get('category', blog.category)
        category, created = Category.objects.get_or_create(category=category)
        blog.category = category
        blog.tags.clear()
        
        for tag in tags_list:
            tag, created = Tag.objects.get_or_create(tag=tag)
            blog.tags.add(tag)
        
        if data.get("img"):
            img = data.get("img")
            blog.img = img
        blog.save()

        serializer = BlogSerializer(blog, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    
# delete a Blog view
@api_view(['DELETE'])
def delete_blog(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# increase the blog views
@api_view(['get'])
def add_views(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog.views += 1
        blog.save()
        return Response(status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    







