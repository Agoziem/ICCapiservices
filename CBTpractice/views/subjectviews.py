from django.shortcuts import render
from ..models import *
from ..serializers import SubjectSerializer, QuestionSerializer, CreateSubjectSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# view to get all the subjects
@swagger_auto_schema(method="get", responses={200: SubjectSerializer(many=True), 404: 'Test Not Found'})
@api_view(['GET'])
@permission_classes([])
def get_subjects(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        subjects = test.testSubject.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching subjects: {str(e)}")
        return Response({'error': 'An error occurred while fetching subjects'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# view to get a single subject
@swagger_auto_schema(method="get", responses={200: SubjectSerializer, 404: 'Subject Not Found'})
@api_view(['GET'])
@permission_classes([])
def get_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        serializer = SubjectSerializer(subject, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error fetching subject: {str(e)}")
        return Response({'error': 'An error occurred while fetching subject'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# view to create a subject
# / //   {
# //     "id": 3,
# //     "testYear": {
# //         "id": 3,
# //         "year": 2021
# //     },
# //     "texttype": {
# //         "id": 4,
# //         "testtype": "WEAC"
# //     },
# //     "testSubject": [
# //         {
# //             "id": 6,
# //             "questions": [],
# //             "subjectduration": 0,
# //             "subjectname": "Mathematics"
# //         },
# //         {
# //             "id": 7,
# //             "questions": [],
# //             "subjectduration": 0,
# //             "subjectname": "English"
# //         },
# //         {
# //             "id": 8,
# //             "questions": [],
# //             "subjectduration": 0,
# //             "subjectname": "Igbo language"
# //         },
# //         {
# //             "id": 9,
# //             "questions": [],
# //             "subjectduration": 0,
# //             "subjectname": "Chemistry"
# //         }
# //     ],
# //     "testorganization": 1
# // }

@swagger_auto_schema(method="post", request_body=CreateSubjectSerializer, responses={201: SubjectSerializer, 404: 'Test Not Found'})
@api_view(['POST'])
def add_subject(request, test_id):
    # Validate input data using serializer
    serializer = CreateSubjectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        test = Test.objects.get(id=test_id)
        
        subjectduration = validated_data.get('subjectduration', 0)
        subjectname = validated_data.get('subjectname')
        
        subject = Subject.objects.create(
            subjectduration=subjectduration, 
            subjectname=subjectname
        )
        
        # Add questions to the subject
        questions_data = validated_data.get('questions', [])
        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                try:
                    question = Question.objects.get(id=question_id)
                    subject.questions.add(question)
                except Question.DoesNotExist:
                    print(f"Question with id {question_id} not found")
                    continue
        
        subject.save()
        test.testSubject.add(subject)
        
        subject_serializer = SubjectSerializer(subject)
        return Response(subject_serializer.data, status=status.HTTP_201_CREATED)
        
    except Test.DoesNotExist:
        return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating subject: {str(e)}")
        return Response({'error': 'An error occurred during subject creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to update a subject
@swagger_auto_schema(method="put", request_body=CreateSubjectSerializer, responses={200: SubjectSerializer, 404: 'Subject Not Found'})
@api_view(['PUT'])
def update_subject(request, subject_id):
    # Validate input data using serializer
    serializer = CreateSubjectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        subject = Subject.objects.get(id=subject_id)
        
        # Update subject fields
        subject.subjectduration = validated_data.get('subjectduration', subject.subjectduration)
        subject.subjectname = validated_data.get('subjectname', subject.subjectname)
        
        # Clear existing questions and add new ones
        subject.questions.clear()
        questions_data = validated_data.get('questions', [])
        for question_data in questions_data:
            question_id = question_data.get('id')
            if question_id:
                try:
                    question = Question.objects.get(id=question_id)
                    subject.questions.add(question)
                except Question.DoesNotExist:
                    print(f"Question with id {question_id} not found")
                    continue
        
        subject.save()
        subject_serializer = SubjectSerializer(subject)
        return Response(subject_serializer.data, status=status.HTTP_200_OK)
        
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating subject: {str(e)}")
        return Response({'error': 'An error occurred during subject update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# view to delete a subject
@swagger_auto_schema(method="delete", responses={204: 'Subject deleted successfully', 404: 'Subject Not Found'})
@api_view(['DELETE'])
def delete_subject(request, subject_id):
    try: 
        subject = Subject.objects.get(id=subject_id) 
        subject.delete()
        return Response({'message': 'Subject deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting subject: {str(e)}")
        return Response({'error': 'An error occurred during subject deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
