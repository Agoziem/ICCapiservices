from django.shortcuts import render
from ..models import *
from ..serializers import SubjectSerializer, QuestionSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# view to get all the subjects
@api_view(['GET'])
def get_subjects(request,test_id):
    try:
        test = Test.objects.get(id=test_id)
        subjects = test.testSubject.all()
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

@api_view(['POST'])
def add_subject(request, test_id):
    data = request.data
    try:
        test = Test.objects.get(id=test_id)
        subjectduration = data.get('subjectduration', 0)
        subjectname = data.get('subjectname', None)
        subject = Subject.objects.create(subjectduration=subjectduration, subjectname=subjectname)
        questions = data.get('questions', [])
        for question in questions:
            question_id = question.get('id', None)
            if question_id:
                question = Question.objects.get(id=question_id)
                subject.questions.add(question)
        subject.save()
        test.testSubject.add(subject)
        subject_serializer = SubjectSerializer(subject)
        return Response(subject_serializer.data,status=status.HTTP_201_CREATED)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    
# view to update a subject
@api_view(['PUT'])
def update_subject(request, subject_id):
    data = request.data
    try:
        subject = Subject.objects.get(id=subject_id)
        subjectduration = data.get('subjectduration', subject.subjectduration)
        subjectname = data.get('subjectname', subject.subjectname)
        subject.subjectduration = subjectduration
        subject.subjectname = subjectname
        questions = data.get('questions', subject.questions.all())
        subject.questions.clear()
        for question in questions:
            question_id = question.get('id', None)
            if question_id:
                question = Question.objects.get(id=question_id)
                subject.questions.add(question)
        subject.save()
        subject_serializer = SubjectSerializer(subject)
        return Response(subject_serializer.data,status=status.HTTP_200_OK)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# view to delete a subject
@api_view(['DELETE'])
def delete_subject(request,subject_id):
    try: 
        subject = Subject.objects.get(id=subject_id) 
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
