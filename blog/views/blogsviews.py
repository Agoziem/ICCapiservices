from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

# get all blogs by an Organization
@api_view(['GET'])
def get_org_blogs(request,organization_id):
    try:
        blogs = Blog.objects.filter(organization=organization_id)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get all blogs by a User
@api_view(['GET'])
def get_blogs(request,user_id):
    try:
        blogs = Blog.objects.filter(author=user_id)
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

# Add a Blog view
@api_view(['POST'])
def add_blog(request,organization_id,user_id):
    data = request.data.copy()
    try:
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=organization_id)
        if data.get('img') == '':
                data['img'] = None
        serializer = BlogSerializer(data=data)
        if serializer.is_valid():
            serializer.save(author=user,organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist or Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a Blog view
@api_view(['PUT'])
def update_blog(request, blog_id):
    data = request.data.copy()
    try:
        blog = Blog.objects.get(id=blog_id)
        if data.get('img') == '':
            data['img'] = None
        serializer = BlogSerializer(instance=blog, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a Blog view
@api_view(['DELETE'])
def delete_blog(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        blog.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)





