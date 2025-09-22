import os
from django.shortcuts import render

from authentication.serializers import SuccessResponseSerializer
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema

# upload image for rich text editor
@swagger_auto_schema(
    method="post",
    request_body=CreateRichTextEditorImagesSerializer,
    responses={
        201: RichTextEditorImagesSerializer(),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_rich_text_image(request):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()
    else:
        data = request.data

    try:
        data = normalize_img_field(data, "image")
        serializer = CreateRichTextEditorImagesSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_image = serializer.save()
        return Response(RichTextEditorImagesSerializer(new_image).data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"Error uploading rich text image: {str(e)}")
        return Response({'error': 'An error occurred during image upload'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# get all images uploaded for rich text editor
@swagger_auto_schema(
    method="get",
    responses={
        200: RichTextEditorImagesSerializer(many=True),
        404: 'Images Not Found'
    }
)
@api_view(['GET'])
def get_rich_text_images(request):
    try:
        images = RichTextEditorImages.objects.all()
        if not images.exists():
            return Response([], status=status.HTTP_200_OK)

        serializer = RichTextEditorImagesSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching rich text images: {str(e)}")
        return Response({'error': 'An error occurred while fetching rich text images'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# delete a rich text editor image
@swagger_auto_schema(
    method="delete",
    responses={
        204: SuccessResponseSerializer,
        404: 'Image Not Found'
    }
)
@api_view(['DELETE'])
def delete_rich_text_image(request):
        """Deletes a file based on its file_url query parameter"""

        file_url = request.query_params.get('file_url')  # Extract file_url from query parameters

        if not file_url:
            return Response({'error': 'file_url parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Extract relative file path
        base_url = settings.DJANGO_IMAGE_URL.rstrip('/')  # Ensure no trailing slash
        if not file_url.startswith(base_url):
            return Response({'error': 'Invalid file URL'}, status=status.HTTP_400_BAD_REQUEST)

        relative_path = file_url.replace(base_url, "").lstrip("/")  # Extract relative path
        relative_path = file_url.split('/media/')[-1]  # gives "files/IMG_...jpg"

        try:
            file_instance = RichTextEditorImages.objects.get(image=relative_path)
            file_path = os.path.join(settings.MEDIA_ROOT, file_instance.image.name)  # Full file path

            # Delete from filesystem
            if os.path.exists(file_path):
                os.remove(file_path)

            # Delete from database
            file_instance.delete()
            return Response({'message': 'File deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

        except RichTextEditorImages.DoesNotExist:
            return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)