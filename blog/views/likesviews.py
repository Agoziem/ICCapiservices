from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()
    
# add a like view
@api_view(['GET'])
def add_like(request, blog_id, user_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        user = User.objects.get(id=user_id)
        blog.likes.add(user)
        return Response(status=status.HTTP_201_CREATED)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a like view
@api_view(['DELETE'])
def delete_like(request, blog_id, user_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        user = User.objects.get(id=user_id)
        blog.likes.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)