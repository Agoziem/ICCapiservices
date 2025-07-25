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
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
        return Response(status=status.HTTP_404_NOT_FOUND)
    

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
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        data = normalize_img_field(data,"logo")
        serializer = OrganizationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    if isinstance(request.data, QueryDict):
        data = request.data.dict()  # Convert QueryDict to a mutable dictionary
    else:
        data = request.data
    try:
        organization = Organization.objects.get(id=organization_id)
        data = normalize_img_field(data,"logo")
        organization_serializer = OrganizationSerializer(instance=organization, data=data)
        if organization_serializer.is_valid():
            organization_serializer.save()
            return Response(organization_serializer.data, status=status.HTTP_200_OK)
        return Response(organization_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# delete an organization view
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Organization Not Found'
    }
)
@api_view(['DELETE'])
def delete_organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

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
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)
        organization.privacy_policy = data.get('privacy_policy', organization.privacy_policy)
        organization.save()
        organization_serializer = OrganizationSerializer(organization, many=False)
        return Response(organization_serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
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
    data = request.data.copy()
    try:
        organization = Organization.objects.get(id=organization_id)
        organization.terms_of_use = data.get('terms_of_use', organization.terms_of_use)
        organization.save()
        organization_serializer = OrganizationSerializer(organization, many=False)
        return Response(organization_serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)