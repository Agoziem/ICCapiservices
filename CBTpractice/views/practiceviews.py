from django.shortcuts import get_object_or_404, render
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from typing import cast
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())

@swagger_auto_schema(
    method="post",
    request_body=StudentTestRequestSerializer,
    responses={
        200: TestSerializer,
        400: 'Bad Request',
        404: 'User or Test Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def get_student_tests(request):
    serializer = StudentTestRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    validated_data = serializer.validated_data

    try:
        user_id = validated_data['user_id']
        test_id = validated_data['test_id']
        subjects_id = [subject['id'] for subject in validated_data.get('examSubjects', [])]

        # Ensure user and test exist
        user = get_object_or_404(User, id=user_id)
        student_test = get_object_or_404(Test, id=test_id)

        # Serialize test
        test_serializer = TestSerializer(student_test)
        serialized_data = test_serializer.data

        # Optionally validate subject IDs exist
        if subjects_id:
            valid_subjects = set(
                Subject.objects.filter(id__in=subjects_id).values_list('id', flat=True)
            )
            serialized_data['testSubject'] = [
                subj for subj in serialized_data['testSubject']
                if subj['id'] in valid_subjects
            ]

        return Response(serialized_data, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error in get_student_tests: {str(e)}")
        return Response(
            {"error": "An error occurred while fetching student tests"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



# view to Submit Student Test
@swagger_auto_schema(
    method="post",
    request_body=SubmitStudentTestSerializer,
    responses={
        200: TestScoreResponseSerializer,
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def submit_student_test(request, organization_id):
    # Validate input data using serializer
    serializer = SubmitStudentTestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        user_id = request.GET.get('user_id')
        if not user_id:
            return Response({'error': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate user exists
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=organization_id)
        
        Score = {}
        Total_test_score = 0
        test_ids = []
        
        if not validated_data:
            return Response({'error': 'Test data is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        for test_data in validated_data:
            test_score = 0
            try:
                test_id = test_data.get('student_test_id')
                student_test = Test.objects.get(id=test_id)
                test_ids.append(student_test.pk)
                
                for question_data in test_data.get('questions', []):
                    question = Question.objects.get(id=question_data.get('question_id'))
                    # get the answer id from question_data and check if it matches the correct answer
                    answer = Answer.objects.get(id=question_data.get('answer_id'))
                    if answer.isCorrect:
                        test_score += question.questionMark
                
                # Get subject name for this test
                if student_test.testSubject.exists():
                    subject_name = student_test.testSubject.first().subjectname
                    Score[subject_name] = test_score
                
                Total_test_score += test_score
            except (Test.DoesNotExist, Question.DoesNotExist) as e:
                print(f"Error processing test/question: {str(e)}")
                continue
            except Exception as e:
                print(f"Error in test processing: {str(e)}")
                continue
        
        Score['Total'] = Total_test_score
        
        # Create test result
        testresult = TestResultSubmissions.objects.create(organization=organization, user=user)
        if test_ids:
            testresult.tests.add(*test_ids)
        
        return Response(Score, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Organization.DoesNotExist:
        return Response({'error': 'Organization not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in submit_student_test: {str(e)}")
        return Response({'error': 'An error occurred while submitting test'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    