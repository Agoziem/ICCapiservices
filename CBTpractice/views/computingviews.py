from django.shortcuts import render
from ..models import *
from ..serializers import CreateTestSerializer, TestSerializer, TestResultSerializer
from rest_framework.decorators import api_view, permission_classes
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
@permission_classes([])
def get_tests(request, organization_id):
    try:
        tests = Test.objects.filter(testorganization=organization_id)
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response({'error': 'Tests not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching tests: {str(e)}")
        return Response({'error': 'An error occurred while fetching tests'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to get a single Test
@swagger_auto_schema(method="get", responses={200: TestSerializer, 404: 'Not Found'})
@api_view(['GET'])
@permission_classes([])
def get_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        serializer = TestSerializer(test, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching test: {str(e)}")
        return Response({'error': 'An error occurred while fetching test'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method="post", request_body=CreateTestSerializer, responses={201: TestSerializer, 400: 'Bad Request'})
@api_view(['POST'])
def add_test(request, organization_id):
    # Validate input data using serializer
    serializer = CreateTestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        organization = Organization.objects.get(id=organization_id)
        test = serializer.save(testorganization=organization)
        return Response(TestSerializer(test).data, status=status.HTTP_201_CREATED)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating test: {str(e)}")
        return Response({'error': 'An error occurred during test creation'}, status=status.HTTP_400_BAD_REQUEST)
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
    # Validate input data using serializer
    serializer = CreateTestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        test = Test.objects.get(id=test_id)
        updated_serializer = CreateTestSerializer(instance=test, data=request.data)
        if updated_serializer.is_valid():
            updated_test = updated_serializer.save()
            return Response(TestSerializer(updated_test).data, status=status.HTTP_200_OK)
        return Response(updated_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating test: {str(e)}")
        return Response({'error': 'An error occurred during test update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        return Response({'message': 'Test deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting test: {str(e)}")
        return Response({'error': 'An error occurred during test deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to get all testResults
@swagger_auto_schema(
    method="get",
    responses={
        200: TestResultSerializer(many=True),
        404: 'TestResults Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_test_results(request, organization_id):
    try:
        testresults = TestResult.objects.filter(organization=organization_id)
        serializer = TestResultSerializer(testresults, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TestResult.DoesNotExist:
        return Response({'error': 'Test results not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching test results: {str(e)}")
        return Response({'error': 'An error occurred while fetching test results'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
