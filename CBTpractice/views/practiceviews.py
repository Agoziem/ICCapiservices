from django.shortcuts import render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# view to get Test peculiar to a Student
@api_view(['POST'])
def get_student_tests(request,organization_id):
    student_tests=[]
    test = {}
    try:
        user_id = request.get('user_id')
        test_type_id = request.get('test_type')
        subjects_Id = request.get('subjects', [])
        year_id = request.get('year')
    except:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    try:
        User.objects.get(id=user_id)
        test_type = TestType.objects.get(id=test_type_id)
        year = Year.objects.get(id=year_id)
        subjects = Subject.objects.filter(id__in=subjects_Id)
        for subject in subjects:
            try:
                test = Test.objects.get(testorganization=organization_id, testSubject=subject, texttype=test_type, testYear=year)
                test['id'] = test.id
                test['questions'] = Question.objects.filter(test=test)
                student_tests.append(test)
            except Test.DoesNotExist:
                continue
        serializer = TestSerializer(student_tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist or TestType.DoesNotExist or Year.DoesNotExist or Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


    
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

    