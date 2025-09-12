from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from utils import normalize_img_field, parse_json_fields
from rest_framework.pagination import PageNumberPagination
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema

class StaffPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000 

# get all staff
@swagger_auto_schema(
    method="get",
    responses={
        200: PaginatedStaffSerializer,
        404: 'Staff Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_staffs(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        staffs = Staff.objects.filter(organization=organization_id).order_by('id')
        
        if not staffs.exists():
            return Response({'error': 'No staff found for this organization'}, status=status.HTTP_404_NOT_FOUND)
            
        paginator = StaffPagination()
        result_page = paginator.paginate_queryset(staffs, request)
        serializer = StaffSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching staff: {str(e)}")
        return Response({'error': 'An error occurred while fetching staff'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
# get a single staff
@swagger_auto_schema(
    method="get",
    responses={
        200: StaffSerializer,
        404: 'Staff Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        serializer = StaffSerializer(staff, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Staff.DoesNotExist:
        return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching staff member: {str(e)}")
        return Response({'error': 'An error occurred while fetching staff member'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# Add a staff view
@swagger_auto_schema(
    method="post",
    request_body=CreateStaffSerializer,
    responses={
        201: StaffSerializer,
        400: 'Bad Request',
        404: 'Organization Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_staff(request, organization_id):
    try:
        # Validate organization exists
        organization = Organization.objects.get(id=organization_id)
        
        # Process form data
        if isinstance(request.data, QueryDict):
            data = request.data.copy()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
            
        # Normalize image field
        data = normalize_img_field(data, "img")
        
        # Validate input data using serializer
        serializer = CreateStaffSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        new_staff = serializer.save(organization=organization)
        return Response(StaffSerializer(new_staff).data, status=status.HTTP_201_CREATED)

    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating staff member: {str(e)}")
        return Response({'error': 'An error occurred during staff creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update a staff view
@swagger_auto_schema(
    method="put",
    request_body=UpdateStaffSerializer,
    responses={
        200: StaffSerializer,
        400: 'Bad Request',
        404: 'Staff Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        
        # Process form data
        if isinstance(request.data, QueryDict):
            data = request.data.copy()  # Convert QueryDict to a mutable dictionary
        else:
            data = request.data
            
        # Normalize image field
        data = normalize_img_field(data, "img")
        
        # Validate input data using serializer
        serializer = UpdateStaffSerializer(instance=staff, data=data)
        serializer.is_valid(raise_exception=True)
        update_staff = serializer.save()
        return Response(StaffSerializer(update_staff).data, status=status.HTTP_200_OK)

    except Staff.DoesNotExist:
        return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating staff member: {str(e)}")
        return Response({'error': 'An error occurred during staff update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# delete a staff view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Staff deleted successfully',
        404: 'Staff Not Found'
    }
)
@api_view(['DELETE'])
def delete_staff(request, staff_id):
    try:
        staff = Staff.objects.get(id=staff_id)
        staff.delete()
        return Response({'message': 'Staff member deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Staff.DoesNotExist:
        return Response({'error': 'Staff member not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting staff member: {str(e)}")
        return Response({'error': 'An error occurred during staff deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)