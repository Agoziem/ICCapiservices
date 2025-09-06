from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view,parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from utils import normalize_img_field
from django.http import QueryDict
from drf_yasg.utils import swagger_auto_schema

# get all organizations
@swagger_auto_schema(
    method="get",
    responses={
        200: OrganizationSerializer(many=True),
        404: 'Organizations Not Found'
    }
)
@api_view(['GET'])
def get_organizations(request):
    try:
        organizations = Organization.objects.all()
        
        if not organizations.exists():
            return Response({'error': 'No organizations found'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching organizations: {str(e)}")
        return Response({'error': 'An error occurred while fetching organizations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# get a single organization
@swagger_auto_schema(
    method="get",
    responses={
        200: OrganizationSerializer(),
        404: 'Organization Not Found'
    }
)
@api_view(['GET'])
def get_organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        serializer = OrganizationSerializer(organization, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching organization: {str(e)}")
        return Response({'error': 'An error occurred while fetching organization'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# Add an organization view
@swagger_auto_schema(
    method="post",
    request_body=OrganizationSerializer,
    responses={
        201: OrganizationSerializer(),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def add_organization(request):
    # Process form data
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
        
    try:
        # Normalize image field
        data = normalize_img_field(data, "logo")
        
        # Validate input data using serializer
        serializer = OrganizationSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"Error creating organization: {str(e)}")
        return Response({'error': 'An error occurred during organization creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update an organization view
@swagger_auto_schema(
    method="put",
    request_body=OrganizationSerializer,
    responses={
        200: OrganizationSerializer(),
        400: 'Bad Request',
        404: 'Organization Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_organization(request, organization_id):
    # Process form data
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
        
    try:
        organization = Organization.objects.get(id=organization_id)
        
        # Normalize image field
        data = normalize_img_field(data, "logo")
        
        # Validate input data using serializer
        organization_serializer = OrganizationSerializer(instance=organization, data=data)
        if not organization_serializer.is_valid():
            return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        organization_serializer.save()
        return Response(organization_serializer.data, status=status.HTTP_200_OK)
        
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating organization: {str(e)}")
        return Response({'error': 'An error occurred during organization update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# delete an organization view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Organization deleted successfully',
        404: 'Organization Not Found'
    }
)
@api_view(['DELETE'])
def delete_organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        organization.delete()
        return Response({'message': 'Organization deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting organization: {str(e)}")
        return Response({'error': 'An error occurred during organization deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# edit the Organization Privacy Policy
@swagger_auto_schema(
    method="put",
    request_body=OrganizationSerializer,
    responses={
        200: OrganizationSerializer(),
        404: 'Organization Not Found'
    }
)
@api_view(['PUT'])
def edit_privacy_policy(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        data = request.data.copy()
        
        # Validate that privacy_policy is provided
        privacy_policy = data.get('privacy_policy')
        if privacy_policy is None:
            return Response({'error': 'Privacy policy content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        organization.privacy_policy = privacy_policy
        organization.save()
        
        organization_serializer = OrganizationSerializer(organization, many=False)
        return Response(organization_serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating privacy policy: {str(e)}")
        return Response({'error': 'An error occurred during privacy policy update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# edit the Organization Terms of Use
@swagger_auto_schema(
    method="put",
    request_body=OrganizationSerializer,
    responses={
        200: OrganizationSerializer(),
        404: 'Organization Not Found'
    }
)
@api_view(['PUT'])
def edit_terms_of_use(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        data = request.data.copy()
        
        # Validate that terms_of_use is provided
        terms_of_use = data.get('terms_of_use')
        if terms_of_use is None:
            return Response({'error': 'Terms of use content is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        organization.terms_of_use = terms_of_use
        organization.save()
        
        organization_serializer = OrganizationSerializer(organization, many=False)
        return Response(organization_serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating terms of use: {str(e)}")
        return Response({'error': 'An error occurred during terms of use update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)