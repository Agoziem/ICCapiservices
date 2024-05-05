from django.shortcuts import render
from ..models import Subject
from ..serializers import SubjectSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# view to get all the subjects
@api_view(['GET'])
def get_subjects(request):
    try:
        subjects = Subject.objects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# view to get a single subject
@api_view(['GET'])
def get_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        serializer = SubjectSerializer(subject, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to create a subject
@api_view(['POST'])
def add_subject(request):
    try:
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to update a subject
@api_view(['PUT'])
def update_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        serializer = SubjectSerializer(instance=subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to delete a subject
@api_view(['DELETE'])
def delete_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)