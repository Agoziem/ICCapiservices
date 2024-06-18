from django.shortcuts import render
from ..models import *
from ..serializers import TestSerializer,TestResultSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


# view to get all the Tests
@api_view(['GET'])
def get_tests(request,organization_id):
    try:
        tests = Test.objects.filter(testorganization=organization_id)
        serializer = TestSerializer(tests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
# view to get a single Test
@api_view(['GET'])
def get_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        serializer = TestSerializer(test, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def add_test(request,organization_id):
    try:
        organization = Organization.objects.get(id=organization_id)
        testyear = request.data.get('testYear', None)
        testtype = request.data.get('texttype', None).upper()
        testsubject = request.data.get('testSubject', [])
        # check if the test already exists
        test = Test.objects.filter(testorganization=organization,testYear__year=testyear,texttype__testtype=testtype)
        if test.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            # create year, testtype and subject
            year = Year.objects.create(year=testyear)
            testType = TestType.objects.create(testtype=testtype)
            subjectsID = []
            for subject in testsubject:
                subject = Subject.objects.create(subjectname=subject)
                subject.save()
                subjectsID.append(subject.id)
            test = Test.objects.create(testorganization=organization,testYear=year,texttype=testType)
            test.testSubject.add(*subjectsID)
            test.save()
            test_serializer = TestSerializer(test, many=False)
            return Response(test_serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# view to update a Test
@api_view(['PUT'])
def update_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        Subject_id = request.data.get('subjectid', test.testSubject.id)
        TestTypeid = request.data.get('testtypeid', test.texttype.id)
        Year_id = request.data.get('yearid', test.testYear.id)
        testtype = TestType.objects.get(id=TestTypeid)
        subject = Subject.objects.get(id=Subject_id)
        year = Year.objects.get(id=Year_id)
        test.testSubject = subject
        test.texttype = testtype
        test.testYear = year
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    test.testMark = request.data.get('mark', test.mark)
    test.testTime = request.data.get('time', test.time)
    questions = request.data.get('questions', [])
    for question in questions:
        question = Question.objects.create(questiontext=question.text,questionMark=question.mark, test=test)
        answers = question.get('answers', [])
        for answer in answers:
            Answer.objects.create(answerText=answer.text, is_correct=answer.is_correct, question=question)
    test.save()
    return Response(status=status.HTTP_200_OK)

# view to delete a Test
@api_view(['DELETE'])
def delete_test(request, test_id):
    try:
        test = Test.objects.get(id=test_id)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Test.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    

# view to get all testResults
@api_view(['GET'])
def get_test_results(request,organization_id):
    try:
        testresults = TestResult.objects.filter(organization=organization_id)
        serializer = TestResultSerializer(testresults, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except TestResult.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
