from django.shortcuts import render
from ..models import Year
from ..serializers import YearsSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# view to get all the years
@api_view(['GET'])
def get_years(request):
    try:
        years = Year.objects.all()
        serializer = YearsSerializer(years, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Year.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# view to get a single year
@api_view(['GET'])
def get_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
        serializer = YearsSerializer(year, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Year.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    
# view to create a year
@api_view(['POST'])
def add_year(request):
    try:
        serializer = YearsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Year.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to update a year
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
        return Response(status=status.HTTP_404_NOT_FOUND)

# view to delete a year
@api_view(['DELETE'])
def delete_year(request, year_id):
    try:
        year = Year.objects.get(id=year_id)
        year.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Year.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
