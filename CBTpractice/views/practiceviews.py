from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
def get_student_tests(request):
    try:
        user_id = request.data.get('user_id')
        test_id = request.data.get('test_id')
        subjects = request.data.get('examSubjects', [])
        subjects_id = [subject.get('id') for subject in subjects]
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        User.objects.get(id=user_id)
        student_test = Test.objects.get(id=test_id)
        Subject.objects.filter(id__in=subjects_id)
        serializer = TestSerializer(student_test)
        serialized_data = serializer.data
        filtered_subjects = [subj for subj in serialized_data['testSubject'] if subj['id'] in subjects_id]
        serialized_data['testSubject'] = filtered_subjects
        return Response(serialized_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Test.DoesNotExist:
        return Response({"error": "Test does not exist"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(str(e))
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
# view to Submit Student Test
@api_view(['POST'])
def submit_student_test(request,organization_id):
    try:
        user_id = request.get('user_id')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    Score = {}
    Total_test_score = 0
    test_ids = []
    if request.data is None or request.data == []:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    for test in request.data:
        test_score = 0
        try:
            test_id = test.get('student_test_id')
            student_test = Test.objects.get(id=test_id)
            test_ids.append(student_test.id)
            for question in test.get('questions', []):
                question = Question.objects.get(id=question.get('question_id'))
                if question.answer.is_correct:
                    test_score += question.score
            Score[student_test.testSubject.subjectname] = test_score
            Total_test_score += test_score
        except:
            continue 
    Score['Total'] = Total_test_score
    testresult = TestResult.objects.create(organization=organization_id, user=user_id)
    testresult.tests.add(*test_ids)
    return Response(Score, status=status.HTTP_200_OK)

    