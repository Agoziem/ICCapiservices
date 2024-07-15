from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field


# get all videos
@api_view(['GET'])
def get_videos(request, organization_id):
    try:
        videos = Video.objects.filter(organization=organization_id).order_by('-updated_at')
        serializer = VideoSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# get a single video
@api_view(['GET'])
def get_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# add a video
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_video(request, organization_id):
    try:
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        thumbnail = request.data.get('thumbnail')
        video = request.data.get('video')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        organization = Organization.objects.get(id=organization_id)
        category = Category.objects.get(id=category)
        video = Video.objects.create(organization=organization, title=title, description=description, category=category, thumbnail=thumbnail, video=video)
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist or Category.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

# update a video
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_video(request, video_id):
    try:
        title = request.data.get('title')
        description = request.data.get('description')
        category = request.data.get('category')
        thumbnail = request.data.get('thumbnail')
        video = request.data.get('video')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        video = Video.objects.get(id=video_id)
        video.title = title
        video.description = description
        video.category = category
        video.thumbnail = thumbnail
        video.video = video
        video.save()
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# delete a video
@api_view(['DELETE'])
def delete_video(request, video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
