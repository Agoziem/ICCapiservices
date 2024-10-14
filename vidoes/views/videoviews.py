from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
import json

# --------------------------------------------------------------------------
# get all videos
# --------------------------------------------------------------------------
class VideoPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
# 
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
    
# --------------------------------------------------------------------------
# get a single video
# --------------------------------------------------------------------------
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
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_video(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)

        # Extract and parse JSON fields from the request data
        parsed_json_fields = {}
        image_fields = ['thumbnail', 'video']
        for field in request.data:
            if field not in image_fields:
                try:
                    parsed_json_fields[field] = json.loads(request.data[field])
                except (json.JSONDecodeError, TypeError):
                    parsed_json_fields[field] = request.data[field]

        # Normalize image fields
        data = request.data
        for field in image_fields:
            if field in data:
                data = normalize_img_field(data, field)
        
        category = Category.objects.get(id=parsed_json_fields['category'].get('id'))

        video = Video.objects.create(
            organization=organization,
            title=parsed_json_fields.get('title', ''),
            description=parsed_json_fields.get('description', ''),
            price=parsed_json_fields.get('price', 0.0),
            free=parsed_json_fields.get('free', False),
            category=category
        )

        # Handle subcategory field
        if 'subcategory' in parsed_json_fields and parsed_json_fields['subcategory']:
            subcategory = SubCategory.objects.get(id=parsed_json_fields['subcategory'].get('id'))
            video.subcategory = subcategory

        # Handle image & file fields
        for field in image_fields:
            if data.get(field):
                setattr(video, field, data.get(field))

        video.save()
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except (Organization.DoesNotExist, Category.DoesNotExist):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# --------------------------------------------------------------------------
# update a video
# --------------------------------------------------------------------------

@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_video(request, video_id):
    data = request.data
    try:
        video = Video.objects.get(id=video_id)

        # Normalize image fields
        image_fields = ['thumbnail', 'video']
        for field in image_fields:
            data = normalize_img_field(data, field)
        
        # Parse JSON fields
        for field in data:
            if field not in image_fields:
                try:
                    data[field] = json.loads(data[field])
                except (json.JSONDecodeError, TypeError):
                    # If field is not JSON, keep it as is
                    pass

        video.title = data.get('title', video.title)
        video.description = data.get('description', video.description)
        video.price = data.get('price', video.price)
        video.free = data.get('free', video.free)

        # Update category field
        if 'category' in data:
            try:
                category_id = data['category'].get('id')
                if category_id:
                    category = Category.objects.get(id=category_id)
                    video.category = category
            except Category.DoesNotExist:
                return Response({"detail": "Category not found."}, status=status.HTTP_400_BAD_REQUEST)
            
        
        # Update subcategory field (optional fields)
        if 'subcategory' in data and data['subcategory']:
                subcategory_id = data['subcategory'].get('id')
                if subcategory_id:
                    subcategory = SubCategory.objects.get(id=subcategory_id)
                    video.subcategory = subcategory
        else:
            video.subcategory = None

        # Handle image fields
        for field in image_fields:
            if field in data:
                setattr(video, field, data.get(field))

        video.save()
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    
    
# --------------------------------------------------------------------------
# delete a video
# --------------------------------------------------------------------------
@api_view(['DELETE'])
def delete_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
