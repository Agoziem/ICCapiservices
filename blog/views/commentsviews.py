from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from typing import cast
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())

class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# get all comments for a blog and paginate them
@swagger_auto_schema(method="get", responses={200: PaginatedCommentSerializer, 404: 'Comments Not Found'})
@api_view(['GET'])
@permission_classes([])
def get_comments(request, blog_id):
    try:
        comments = Comment.objects.filter(blog=blog_id).order_by('-updated_at')
        paginator = CommentPagination()
        result_page = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Comment.DoesNotExist:
        return Response({'error': 'Comments not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching comments: {str(e)}")
        return Response({'error': 'An error occurred while fetching comments'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# add a comment view
@swagger_auto_schema(method="post", request_body=CreateCommentSerializer, responses={201: CommentSerializer, 404: 'Blog or User Not Found', 400: 'Bad Request'})
@api_view(['POST'])
def add_comment(request, blog_id, user_id):
    # Validate input data using serializer
    serializer = CreateCommentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        blog = Blog.objects.get(id=blog_id)
        user = User.objects.get(id=user_id)
        comment = Comment.objects.create(
            blog=blog, 
            user=user, 
            comment=validated_data['comment']
        )
        comment_serializer = CommentSerializer(comment, many=False)
        return Response(comment_serializer.data, status=status.HTTP_201_CREATED)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating comment: {str(e)}")
        return Response({'error': 'An error occurred during comment creation'}, status=status.HTTP_400_BAD_REQUEST)
    
# update a comment view
@swagger_auto_schema(method="put", request_body=UpdateCommentSerializer, responses={200: CommentSerializer, 404: 'Comment Not Found'})
@api_view(['PUT'])
def update_comment(request, comment_id):
    # Validate input data using serializer
    serializer = UpdateCommentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.comment = validated_data.get('comment', comment.comment)
        comment.save()
        comment_serializer = CommentSerializer(comment, many=False)
        return Response(comment_serializer.data, status=status.HTTP_200_OK)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating comment: {str(e)}")
        return Response({'error': 'An error occurred during comment update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
      
# delete a comment view
@swagger_auto_schema(method="delete", responses={204: 'No Content', 404: 'Comment Not Found'})
@api_view(['DELETE'])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting comment: {str(e)}")
        return Response({'error': 'An error occurred during comment deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    