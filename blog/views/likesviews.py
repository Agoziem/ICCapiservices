from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

    
# add a like view
@api_view(['POST'])
def add_like(request, blog_id, user_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        user = User.objects.get(id=user_id)
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user, blog=blog)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a like view
@api_view(['DELETE'])
def delete_like(request, like_id):
    try:
        like = Like.objects.get(id=like_id)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Like.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)