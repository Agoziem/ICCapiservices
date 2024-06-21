from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()


# get all comments for a blog
@api_view(['GET'])
def get_comments(request, blog_id):
    try:
        comments = Comment.objects.filter(blog=blog_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# add a comment view
@api_view(['POST'])
def add_comment(request, blog_id, user_id):
    try:
        blog = Blog.objects.get(id=blog_id)
        user = User.objects.get(id=user_id)
        comment = Comment.objects.create(blog=blog, user=user, comment=request.data['comment'])
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Blog.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# update a comment view
@api_view(['PUT'])
def update_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.comment = request.data.get('comment', comment.comment)
        comment.save()
        serializer = CommentSerializer(comment, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
      
# delete a comment view
@api_view(['DELETE'])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Comment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    