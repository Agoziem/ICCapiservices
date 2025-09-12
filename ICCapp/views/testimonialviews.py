from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema

# --------------------------------------------------------------------------
# get all testimonials
# --------------------------------------------------------------------------
class TestimonialPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedTestimonialSerializer,
        404: 'Testimonials Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_testimonials(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        testimonials = Testimonial.objects.filter(organization=organization_id).order_by('-created_at')
        
        if not testimonials.exists():
            return Response({'error': 'No testimonials found for this organization'}, status=status.HTTP_404_NOT_FOUND)
            
        paginator = TestimonialPagination()
        result_page = paginator.paginate_queryset(testimonials, request)
        serializer = TestimonialSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching testimonials: {str(e)}")
        return Response({'error': 'An error occurred while fetching testimonials'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# get a single testimonial
@swagger_auto_schema(
    method="get",
    responses={
        200: TestimonialSerializer(),
        404: 'Testimonial Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        serializer = TestimonialSerializer(testimonial, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# Add a testimonial view
@swagger_auto_schema(
    method="post",
    request_body=CreateTestimonialSerializer,
    responses={
        201: TestimonialSerializer(),
        400: 'Bad Request',
        404: 'Organization Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_testimonial(request, organization_id):
    try:
        if isinstance(request.data, QueryDict):
            data = request.data.copy()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        organization = Organization.objects.get(id=organization_id)
        data = normalize_img_field(data,"img")

        serializer = CreateTestimonialSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_testimonial = serializer.save(organization=organization)
        return Response(TestimonialSerializer(new_testimonial).data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# update a testimonial view
@swagger_auto_schema(
    method="put",
    request_body=UpdateTestimonialSerializer,
    responses={
        200: TestimonialSerializer(),
        400: 'Bad Request',
        404: 'Testimonial Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        if isinstance(request.data, QueryDict):
            data = request.data.copy()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
        data = normalize_img_field(data,"img")
        serializer = UpdateTestimonialSerializer(instance=testimonial, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_testimonial = serializer.save()
        return Response(TestimonialSerializer(updated_testimonial).data, status=status.HTTP_200_OK)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
# delete a testimonial view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Testimonial Not Found'
    }
)
@api_view(['DELETE'])
def delete_testimonial(request, testimonial_id):
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Testimonial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)