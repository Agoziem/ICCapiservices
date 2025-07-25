from django.shortcuts import render
from ..models import *
from ..serializers import CreateTestSerializer, TestSerializer, TestResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema


# view to get all the Tests
@swagger_auto_schema(
    method="get",
    responses={
        200: TestSerializer(many=True),
        404: 'Not Found'
    }
)
@api_view(['GET'])
def get_tests(request, organization_id):
    try:
        tests = Test.objects.filter(testorganization=organization_id)
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# view to get a single Test


@swagger_auto_schema(method="get", responses={200: TestSerializer, 404: 'Not Found'})
@api_view(['GET'])
def get_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        serializer = TestSerializer(test, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(method="post", request_body=CreateTestSerializer, responses={201: TestSerializer, 400: 'Bad Request'})
@api_view(['POST'])
def add_test(request, organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        serializer = CreateTestSerializer(data=request.data)
        if serializer.is_valid():
            test = serializer.save(testorganization=organization)
            return Response(TestSerializer(test).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)


# view to update a Test
@swagger_auto_schema(
    method="put",
    request_body=CreateTestSerializer,
    responses={
        200: 'Test updated successfully',
        404: 'Test Not Found'
    }
)
@api_view(['PUT'])
def update_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        serializer = CreateTestSerializer(instance=test, data=request.data)
        if serializer.is_valid():
            updated_test = serializer.save()
            return Response(TestSerializer(updated_test).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# view to delete a Test


@swagger_auto_schema(
    method="delete",
    responses={
        204: 'Test deleted successfully',
        404: 'Test Not Found'
    }
)
@api_view(['DELETE'])
def delete_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


# view to get all testResults
@swagger_auto_schema(
    method="get",
    responses={
        200: TestResultSerializer(many=True),
        404: 'TestResults Not Found'
    }
)
@api_view(['GET'])
def get_test_results(request, organization_id):
    try:
        testresults = TestResult.objects.filter(organization=organization_id)
        serializer = TestResultSerializer(testresults, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TestResult.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
