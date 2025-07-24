from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# view to get all Testtype
@swagger_auto_schema(method="get", responses={200: TestTypeSerializer(many=True), 404: 'TestTypes Not Found'})
@api_view(['GET'])
def get_testtypes(request):
    try:
        testtypes = TestType.objects.all()
        serializer = TestTypeSerializer(testtypes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TestType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to get a single Testtype
@swagger_auto_schema(method="get", responses={200: TestTypeSerializer, 404: 'TestType Not Found'})
@api_view(['GET'])
def get_testtype(request, testtype_id):
    try:
        testtype = TestType.objects.get(id=testtype_id)
        serializer = TestTypeSerializer(testtype, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TestType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to create a Testtype
@swagger_auto_schema(method="post", request_body=TestTypeSerializer, responses={201: TestTypeSerializer, 400: 'Bad Request'})
@api_view(['POST'])
def add_testtype(request):
    try:
        serializer = TestTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except TestType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to update a Testtype
@swagger_auto_schema(method="put", request_body=TestTypeSerializer, responses={200: TestTypeSerializer, 400: 'Bad Request', 404: 'TestType Not Found'})
@api_view(['PUT'])
def update_testtype(request, testtype_id):
    try:
        testtype = TestType.objects.get(id=testtype_id)
        serializer = TestTypeSerializer(instance=testtype, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except TestType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# view to delete a Testtype
@swagger_auto_schema(method="delete", responses={204: 'TestType deleted successfully', 404: 'TestType Not Found'})
@api_view(['DELETE'])
def delete_testtype(request, testtype_id):
    try:
        testtype = TestType.objects.get(id=testtype_id)
        testtype.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except TestType.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)