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
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)
        data = normalize_img_field(data,"thumbnail")
        data = normalize_img_field(data,"video")
        category = Category.objects.get(id=data.get('category', None))
        video = Video.objects.create(
            organization=organization,
            title=data.get('title', ''),
            description=data.get('description', ''),
            category=category
        )
        if data.get('thumbnail'):
            video.thumbnail = data.get('thumbnail')
        if data.get('video'):
            video.video = data.get('video')
        video.save()
        serializer = VideoSerializer(video, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist or Category.DoesNotExist:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)

# update a video
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_video(request, video_id):
    data = request.data.copy()
    try:
        video = Video.objects.get(id=video_id)
        try:
            data = normalize_img_field(data,"thumbnail")
            data = normalize_img_field(data,"video")
            video.title = data.get('title', video.title)
            video.description = data.get('description', video.description)
            category = Category.objects.get(id=data.get('category', video.category.category))
            video.category = category
            if data.get('thumbnail'):
                video.thumbnail = data.get('thumbnail')
            if data.get('video'):
                video.video = data.get('video')
            video.save()
        except Category.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
