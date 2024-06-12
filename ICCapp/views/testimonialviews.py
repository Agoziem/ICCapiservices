from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# get all testimonials
@api_view(['GET'])
def get_testimonials(request, organization_id):
    try:
        testimonials = Testimonial.objects.filter(organization=organization_id)
        serializer = TestimonialSerializer(testimonials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
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
def add_testimonial(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        serializer = TestimonialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(organization=organization)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# update a testimonial view
@api_view(['PUT'])
def update_testimonial(request, testimonial_id):
    print(testimonial_id)
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        serializer = TestimonialSerializer(instance=testimonial, data=request.data)
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