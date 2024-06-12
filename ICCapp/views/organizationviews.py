from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# get all organizations
@api_view(['GET'])
def get_organizations(request):
    try:
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# get a single organization
@api_view(['GET'])
def get_organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        serializer = OrganizationSerializer(organization, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# Add an organization view
@api_view(['POST'])
def add_organization(request):
    try:
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# update an organization view
@api_view(['PUT'])
def update_organization(request, organization_id):
    data = request.data
    try:
        organization = Organization.objects.get(id=organization_id)
        fields_to_update = ['Organizationlogo', 'name', 'description', 'vision', 'mission', 'email', 'phone', 'address']
        for field in fields_to_update:
            if field in data:
                setattr(organization, field, data[field])
        organization.save()
        organization_serializer = OrganizationSerializer(organization, many=False)
        return Response(organization_serializer.data,status=status.HTTP_200_OK)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# delete an organization view
@api_view(['DELETE'])
def delete_organization(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Organization.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)