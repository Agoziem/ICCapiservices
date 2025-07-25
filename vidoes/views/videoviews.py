from ..models import Category, Video, SubCategory
from ICCapp.models import Organization
from ..serializers import VideoSerializer, CategorySerializer, SubCategorySerializer, CreateVideoSerializer, UpdateVideoSerializer
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field,parse_json_fields
import json
from django.db.models import Count
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema
# --------------------------------------------------------------------------
# get all videos
# --------------------------------------------------------------------------
class VideoPagination(PageNumberPagination):

    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
# 
@swagger_auto_schema(
    method='get',
    operation_description="Get all videos for a specific organization, with optional category filtering",
    responses={
        200: VideoSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_videos(request, organization_id):
    try:
        category = request.GET.get('category', None)
        if category and category != "All":
            video_category = Category.objects.get(category=category)
            videos = Video.objects.filter(organization=organization_id, category=video_category).order_by('-updated_at')
        else:
            videos = Video.objects.filter(organization=organization_id).order_by('-updated_at')
        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@swagger_auto_schema(
    method='get',
    operation_description="Get trending videos for an organization, sorted by number of watchers",
    responses={
        200: VideoSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_trendingvideos(request, organization_id):
    try:
        category = request.GET.get('category', None)

        if category and category != "All":
            video_category = Category.objects.get(category=category)
            videos = Video.objects.filter(
                organization=organization_id, category=video_category
            ).annotate(
                watchers_count=Count('userIDs_that_bought_this_video')
            ).filter(
                watchers_count__gt=0  # Exclude videos with no watchers
            ).order_by('-watchers_count', '-updated_at')
        else:
            videos = Video.objects.filter(
                organization=organization_id
            ).annotate(
                watchers_count=Count('userIDs_that_bought_this_video')
            ).filter(
                watchers_count__gt=0  # Exclude videos with no watchers
            ).order_by('-watchers_count', '-updated_at')

        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)



    
@swagger_auto_schema(
    method='get',
    operation_description="Get videos purchased by a specific user in an organization",
    responses={
        200: VideoSerializer(many=True),
        404: "Not found"
    }
)
@api_view(['GET'])
def get_user_videos(request, organization_id, user_id):
    try:
        category = request.GET.get('category', None)

        # Filter videos where the user exists in userIDs_that_bought_this_video (ManyToManyField)
        if category and category != "All":
            video_category = Category.objects.get(category=category)
            videos = Video.objects.filter(
                organization=organization_id,
                category=video_category,
                userIDs_that_bought_this_video__id=user_id
            ).order_by('-updated_at')
        else:
            videos = Video.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_video__id=user_id
            ).order_by('-updated_at')

        paginator = VideoPagination()
        result_page = paginator.paginate_queryset(videos, request)
        serializer = VideoSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    
# --------------------------------------------------------------------------
# get a single video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video by ID",
    responses={
        200: VideoSerializer,
        404: "Video not found"
    }
)
@api_view(['GET'])
def get_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# --------------------------------------------------------------------------
# get a video by token
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get details of a specific video by token",
    responses={
        200: VideoSerializer,
        404: "Video not found"
    }
)
@api_view(['GET'])
def get_video_token(request, videotoken):
    try:
        video = Video.objects.get(video_token=videotoken)
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------------------------------  
# add a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Add a new video to an organization",
    request_body=CreateVideoSerializer,
    responses={
        201: VideoSerializer,
        400: "Bad request"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_video(request, organization_id):
    try:
        if isinstance(request.data, QueryDict):
            data = request.data.dict()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data

        # Normalize image fields
        image_fields = ['thumbnail', 'video']
        for field in image_fields:
            if field in data:
                data = normalize_img_field(data, field)

        # Extract and parse JSON fields from the request data
        parsed_json_fields = parse_json_fields(data)
        
        # serialize the field
        serializer = VideoSerializer(data=parsed_json_fields)
        if serializer.is_valid():

            video = serializer.save()

            # Retrieve the Organization as well
            video.organization = Organization.objects.get(id=parsed_json_fields['organization'])

            # Handle category field
            video.category = Category.objects.get(id=parsed_json_fields['category'].get('id'))

            # Handle subcategory field
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
                video.subcategory = subcategory

            video.save()
            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except (Organization.DoesNotExist, Category.DoesNotExist):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------------------------------
# update a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update an existing video",
    request_body=UpdateVideoSerializer,
    responses={
        201: VideoSerializer,
        400: "Bad request",
        404: "Video not found"
    },
    parser_classes=[MultiPartParser, FormParser]
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_video(request, video_id):
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        video = Video.objects.get(id=video_id)
        # Normalize image fields
        image_fields = ['thumbnail', 'video']
        for field in image_fields:
            data = normalize_img_field(data, field)
        
        # Extract and parse JSON fields from the request data
        parsed_json_fields = parse_json_fields(data)

        # serialize the field
        serializer = VideoSerializer(video,data=parsed_json_fields)
        if serializer.is_valid():
            video = serializer.save()

            # Retrieve the Organization as well
            video.organization = Organization.objects.get(id=parsed_json_fields['organization'])

            # Update category field
            if 'category' in parsed_json_fields:
                try:
                    category_id = parsed_json_fields['category'].get('id')
                    if category_id:
                        category = Category.objects.get(id=category_id)
                        video.category = category
                except Category.DoesNotExist:
                    return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
                
            # Update subcategory field (optional fields)
            if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
                    subcategory_id = parsed_json_fields['subcategory'].get('id')
                    if subcategory_id:
                        subcategory = SubCategory.objects.get(id=subcategory_id)
                        video.subcategory = subcategory
            else:
                video.subcategory = None

            video.save()
            return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Category.DoesNotExist or Video.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    
# --------------------------------------------------------------------------
# delete a video
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a video",
    responses={
        204: "No Content - Video successfully deleted",
        404: "Video not found"
    }
)
@api_view(['DELETE'])
def delete_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
