from django.shortcuts import render
from ..models import Year
from ..serializers import YearsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# view to get all the years
@swagger_auto_schema(method="get", responses={200: YearsSerializer(many=True), 404: 'Years Not Found'})
@api_view(['GET'])
def get_years(request):
    try:
        years = Year.objects.all()
        if not years.exists():
            return Response({'error': 'No years found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = YearsSerializer(years, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error fetching years: {str(e)}")
        return Response({'error': 'An error occurred while fetching years'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to get a single year
@swagger_auto_schema(method="get", responses={200: YearsSerializer, 404: 'Year Not Found'})
@api_view(['GET'])
def get_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
        serializer = YearsSerializer(year, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Year.DoesNotExist:
        return Response({'error': 'Year not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching year: {str(e)}")
        return Response({'error': 'An error occurred while fetching year'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# view to create a year
@swagger_auto_schema(method="post", request_body=YearsSerializer, responses={201: YearsSerializer, 400: 'Bad Request'})
@api_view(['POST'])
def add_year(request):
    # Validate input data using serializer
    serializer = YearsSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error creating year: {str(e)}")
        return Response({'error': 'An error occurred during year creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# view to update a year
@swagger_auto_schema(method="put", request_body=YearsSerializer, responses={200: YearsSerializer, 400: 'Bad Request', 404: 'Year Not Found'})
@api_view(['PUT'])
def update_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
        serializer = YearsSerializer(instance=year, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Year.DoesNotExist:
        return Response({'error': 'Year not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating year: {str(e)}")
        return Response({'error': 'An error occurred during year update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to delete a year
@swagger_auto_schema(method="delete", responses={204: 'Year deleted successfully', 404: 'Year Not Found'})
@api_view(['DELETE'])
def delete_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
        year.delete()
        return Response({'message': 'Year deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Year.DoesNotExist:
        return Response({'error': 'Year not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting year: {str(e)}")
        return Response({'error': 'An error occurred during year deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
