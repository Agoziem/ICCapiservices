from typing import List, Any, Optional, cast
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone

from ..models import Test, TestResult, Subject, Question, Answer
from ..schemas import (
    QuestionSchema, StudentTestSchema, StudentTestDetailSchema, StudentTestRequestSchema, SubjectSchema,
    TestSubmissionSchema, SubmitStudentTestSchema, TestScoreResponseSchema,
    TestResultSchema, TestResultListResponseSchema,
    SuccessResponseSchema, ErrorResponseSchema
)
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())


@api_controller('/practice', tags=['CBT Practice'])
class PracticeController:

    @route.get('/available-tests')
    def get_available_tests(self, year_id: Optional[int] = None, test_type_id: Optional[int] = None):
        """Get all available tests for practice"""
        tests = Test.objects.select_related(
            'testYear', 'texttype').prefetch_related('testSubject')

        if year_id:
            tests = tests.filter(testYear_id=year_id)
        if test_type_id:
            tests = tests.filter(texttype_id=test_type_id)

        test_list = []
        for test in tests:
            subjects = []
            total_questions = 0
            total_marks = 0
            total_duration = 0

            for subject in test.testSubject.all():
                question_count = subject.questions.count()
                marks = subject.questions.aggregate(
                    total=Sum('questionMark'))['total'] or 0

                subjects.append({
                    'id': subject.id,
                    'subjectname': subject.subjectname,
                    'subjectduration': subject.subjectduration,
                    'questions_count': question_count
                })

                total_questions += question_count
                total_marks += marks
                total_duration += subject.subjectduration

            test_list.append({
                'test_id': test.pk,
                'test_name': f"{test.testYear.year if test.testYear else ''} {test.texttype.testtype if test.texttype else ''} Test",
                'subjects': subjects,
                'total_questions': total_questions,
                'total_marks': total_marks,
                'duration': total_duration
            })

        return test_list

    @route.post('/start-test', response=StudentTestDetailSchema, permissions=[IsAuthenticated])
    def start_test(self, payload: StudentTestRequestSchema):
        """Start a practice test for a student"""
        test = get_object_or_404(Test, id=payload.test_id)
        user = get_object_or_404(User, id=payload.user_id)

        # Create or get existing test result
        test_result, created = TestResult.objects.get_or_create(
            user=user,
            defaults={'started_at': timezone.now()}
        )

        if test not in test_result.tests.all():
            test_result.tests.add(test)

        # Get all questions for the test
        questions = []
        total_questions = 0
        total_marks = 0
        time_limit = 0

        for subject in test.testSubject.all():
            subject_questions = subject.questions.prefetch_related(
                'answers').all()
            questions.extend(subject_questions)
            total_questions += subject_questions.count()
            total_marks += sum(q.questionMark for q in subject_questions)
            time_limit += subject.subjectduration

        return {
            'test': test,
            'questions': questions,
            'total_questions': total_questions,
            'total_marks': total_marks,
            'time_limit': time_limit
        }

    @route.post('/submit-test', response=TestScoreResponseSchema, permissions=[IsAuthenticated])
    def submit_test(self, payload: SubmitStudentTestSchema):
        """Submit test answers and calculate score"""
        total_score = 0
        subject_scores = {}

        for submission in payload.submissions:
            test_result = get_object_or_404(
                TestResult, id=submission.student_test_id)

            for question_answer in submission.questions:
                question = get_object_or_404(
                    Question, id=question_answer.question_id)

                # Find the subject for this question
                subject = question.subject_set.first()  # type: ignore
                subject_name = subject.subjectname if subject else "Unknown"

                if subject_name not in subject_scores:
                    subject_scores[subject_name] = 0

                # Check if answer is correct
                if question_answer.selected_answer_id:
                    selected_answer = get_object_or_404(
                        Answer, id=question_answer.selected_answer_id)
                    if selected_answer.isCorrect:
                        points = question.questionMark
                        total_score += points
                        subject_scores[subject_name] += points

            # Update test result
            test_result.mark = total_score
            test_result.save()

        return {
            'Total': total_score,
            'subject_scores': subject_scores
        }

    @route.get('/my-results', response=TestResultListResponseSchema, permissions=[IsAuthenticated])
    def get_my_test_results(self, request):
        """Get all test results for the current user"""
        test_results = TestResult.objects.filter(
            user=request.user).prefetch_related('tests')
        return {"test_results": test_results}

    @route.get('/result/{result_id}', response=TestResultSchema, permissions=[IsAuthenticated])
    def get_test_result(self, request, result_id: int):
        """Get detailed test result"""
        test_result = get_object_or_404(
            TestResult.objects.prefetch_related(
                'tests__testSubject__questions__answers'),
            id=result_id,
            user=request.user
        )
        return test_result


@api_controller('/computing', tags=['CBT Computing'])
class ComputingController:

    @route.get('/tests', response=List[StudentTestSchema])
    def get_computed_tests(request, year_id: Optional[int] = None, test_type_id: Optional[int] = None):
        """
        Get all tests filtered by optional year_id and test_type_id.
        """
        queryset = Test.objects.all()

        if year_id is not None:
            queryset = queryset.filter(testYear__id=year_id)

        if test_type_id is not None:
            queryset = queryset.filter(texttype__id=test_type_id)

        queryset = queryset.select_related(
            'testYear', 'texttype').prefetch_related('testSubject')

        return [StudentTestSchema.model_validate(test) for test in queryset]

    @route.get('/subjects', response=List[SubjectSchema])
    def get_computed_subjects(self, subject_name: Optional[str] = None):
        """Get all computed subjects of subjectname"""

        computing_subjects = Subject.objects.annotate(
            questions_count=Count('questions'))

        if subject_name:
            computing_subjects = computing_subjects.filter(
                subjectname__icontains=subject_name)

        return [
            {
                'id': subject.pk,
                'subjectname': subject.subjectname,
                'subjectduration': subject.subjectduration,
                'questions_count': subject.questions_count  # type: ignore
            }
            for subject in computing_subjects
        ]

    @route.get('/practice-questions', response=List[QuestionSchema])
    def get_computed_practice_questions(self, limit: Optional[int] = 10):
        """Get random computing questions for practice"""
        questions = Question.objects.all().prefetch_related(
            'answers').order_by('?')[:limit]

        return [QuestionSchema.model_validate(q) for q in questions]
