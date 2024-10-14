from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
from rest_framework.pagination import PageNumberPagination

# --------------------------------------------------------------------------
# get all videos
# --------------------------------------------------------------------------
class TestimonialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@api_view(['GET'])
def get_testimonials(request, organization_id):
    try:
        testimonials = Testimonial.objects.filter(organization=organization_id).order_by('-created_at')
        paginator = TestimonialPagination()
        result_page = paginator.paginate_queryset(testimonials, request)
        serializer = TestimonialSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    
# get a single testimonial
@api_view(['GET'])
def get_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        serializer = TestimonialSerializer(testimonial, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a testimonial view
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_testimonial(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        data = request.data.copy()
        data = normalize_img_field(data,"img")
        serializer = TestimonialSerializer(data=data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a testimonial view
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        data = request.data.copy()
        data = normalize_img_field(data,"img")
        serializer = TestimonialSerializer(instance=testimonial, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# delete a testimonial view
@api_view(['DELETE'])
def delete_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)