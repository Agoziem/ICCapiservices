from django.shortcuts import get_object_or_404
from ..models import Category, Video, SubCategory
from ICCapp.models import Organization
from ..serializers import PaginatedVideoSerializer, VideoSerializer, CategorySerializer, SubCategorySerializer, CreateVideoSerializer, UpdateVideoSerializer
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from utils import normalize_img_field, parse_json_fields
import json
from django.db.models import Count
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth import get_user_model

User = get_user_model()

# --------------------------------------------------------------------------
# Video Pagination Class
# --------------------------------------------------------------------------
class VideoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

# --------------------------------------------------------------------------
# Get all videos for organization
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get all videos for a specific organization, with optional category filtering",
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description="Category name filter", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: PaginatedVideoSerializer,
        404: "Organization not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_videos(request, organization_id):
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
                video_category = Category.objects.get(category=category)
                videos = Video.objects.filter(organization=organization_id, category=video_category).order_by('-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            videos = Video.objects.filter(organization=organization_id).order_by('-updated_at')
        
        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        print(f"Error in get_videos: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get trending videos
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get trending videos for an organization, sorted by number of watchers",
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description="Category name filter", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: PaginatedVideoSerializer,
        404: "Organization not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_trendingvideos(request, organization_id):
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
                video_category = Category.objects.get(category=category)
                videos = Video.objects.filter(
                    organization=organization_id, category=video_category
                ).annotate(
                    watchers_count=Count('userIDs_that_bought_this_video')
                ).filter(
                    watchers_count__gt=0
                ).order_by('-watchers_count', '-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            videos = Video.objects.filter(
                organization=organization_id
            ).annotate(
                watchers_count=Count('userIDs_that_bought_this_video')
            ).filter(
                watchers_count__gt=0
            ).order_by('-watchers_count', '-updated_at')

        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        print(f"Error in get_trendingvideos: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get user videos
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get videos purchased by a specific user in an organization",
    manual_parameters=[
        openapi.Parameter('category', openapi.IN_QUERY, description="Category name filter", type=openapi.TYPE_STRING),
        openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
    ],
    responses={
        200: PaginatedVideoSerializer,
        404: "Organization or user not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_user_videos(request, organization_id, user_id):
    try:
        # Validate organization_id
        if not organization_id or not str(organization_id).isdigit():
            return Response({'error': 'Invalid organization ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user_id
        if not user_id or not str(user_id).isdigit():
            return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate user exists
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        category = request.GET.get('category', None)

        if category and category != "All":
            # Validate category exists
            try:
                video_category = Category.objects.get(category=category)
                videos = Video.objects.filter(
                    organization=organization_id,
                    category=video_category,
                    userIDs_that_bought_this_video__id=user_id
                ).order_by('-updated_at')
            except Category.DoesNotExist:
                return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            videos = Video.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_video__id=user_id
            ).order_by('-updated_at')

        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Exception as e:
        print(f"Error in get_user_videos: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get a video by id
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video by ID",
    responses={
        200: VideoSerializer,
        404: "Video not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_video(request, video_id):
    try:
        # Validate video_id
        if not video_id or not str(video_id).isdigit():
            return Response({'error': 'Invalid video ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate video exists
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_video: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get a video by token
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video by token",
    responses={
        200: VideoSerializer,
        404: "Video not found",
        400: "Bad request"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_video_token(request, videotoken):
    try:
        # Validate video token
        if not videotoken or not videotoken.strip():
            return Response({'error': 'Invalid video token'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate video exists
        try:
            video = Video.objects.get(video_token=videotoken)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error in get_video_token: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Add a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Add a new video to an organization",
    request_body=CreateVideoSerializer,
    responses={
        201: VideoSerializer,
        404: "Organization not found",
        400: "Bad request"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_video(request, organization_id):
    try:
        # Validate organization_id
        if not organization_id or not str(organization_id).isdigit():
            return Response({'error': 'Invalid organization ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate organization exists
        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(request.data, QueryDict):
            data = request.data.copy()
        else:
            data = request.data

        # Normalize image fields
        image_fields = ['thumbnail', 'video']
        for field in image_fields:
            if field in data:
                data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the request data
        parsed_json_fields = parse_json_fields(data)
        
        # Validate using serializer
        serializer = CreateVideoSerializer(data=parsed_json_fields)
        serializer.is_valid(raise_exception=True)

        # Validate and set category
        category_data = parsed_json_fields.get('category')
        if not category_data:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
        category = None
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

        # Handle optional subcategory field
        subcategory = None
        if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
            subcategory_data = parsed_json_fields['subcategory']
            subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
            if subcategory_id:
                try:
                    subcategory = SubCategory.objects.get(id=subcategory_id)
                except SubCategory.DoesNotExist:
                    return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)

        new_video = serializer.save(
            organization=organization,
            category=category,
            subcategory=subcategory
        )
        return Response(VideoSerializer(new_video).data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in add_video: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Update a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing video",
    request_body=UpdateVideoSerializer,
    responses={
        200: VideoSerializer,
        404: "Video not found",
        400: "Bad request"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_video(request, video_id):
    try:
        # Validate video_id
        if not video_id or not str(video_id).isdigit():
            return Response({'error': 'Invalid video ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate video exists
        video = Video.objects.filter(id=video_id).first()
        if not video:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate input data
        if not request.data:
            return Response({'error': 'Request body is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if isinstance(request.data, QueryDict):
            data = request.data.copy()
        else:
            data = request.data
        
        # Normalize image fields
        image_fields = ['thumbnail', 'video']
        for field in image_fields:
            data = normalize_img_field(data, field)
        
        # Extract and parse JSON fields from the request data
        parsed_json_fields = parse_json_fields(data)

        # Validate using serializer
        removed_organization = parsed_json_fields.pop('organization', None)
        removed_category = parsed_json_fields.pop('category', None)
        removed_subcategory = parsed_json_fields.pop('subcategory', None)
        serializer = UpdateVideoSerializer(video, data=parsed_json_fields)
        serializer.is_valid(raise_exception=True)

        # Validate and set organization if provided
        if removed_organization is not None:
            try:
                organization = Organization.objects.get(id=removed_organization)
                video.organization = organization
            except Organization.DoesNotExist:
                return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update category field if provided
        if removed_category is not None:
            category_data = removed_category
            category_id = category_data.get('id') if isinstance(category_data, dict) else category_data
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    video.category = category
                except Category.DoesNotExist:
                    return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
                
        # Update subcategory field (optional)
        if removed_subcategory is not None:
            if removed_subcategory:
                subcategory_data = removed_subcategory
                subcategory_id = subcategory_data.get('id') if isinstance(subcategory_data, dict) else subcategory_data
                if subcategory_id:
                    try:
                        subcategory = SubCategory.objects.get(id=subcategory_id)
                        video.subcategory = subcategory
                    except SubCategory.DoesNotExist:
                        return Response({'error': 'Subcategory not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                video.subcategory = None

        updated_video = serializer.save()
        return Response(VideoSerializer(updated_video).data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'error': 'Validation error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in update_video: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Delete a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a video",
    responses={
        204: "No Content - Video successfully deleted",
        404: "Video not found",
        400: "Bad request"
    }
)
@api_view(['DELETE'])
def delete_video(request, video_id):
    try:
        # Validate video_id
        if not video_id or not str(video_id).isdigit():
            return Response({'error': 'Invalid video ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate video exists
        try:
            video = Video.objects.get(id=video_id)
        except Video.DoesNotExist:
            return Response({'error': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)
        
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"Error in delete_video: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
