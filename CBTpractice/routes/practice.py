from typing import List, Any, Optional, cast
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from ninja_jwt.authentication import JWTAuth
from ..models import Test, TestResult, Question, Answer
from ..schemas import (
    StudentsTestListingSchema,
    StudentTestRequestSchema,
    TestSubmissionSchema,
    TestResultSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())


class PracticePagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/practice", tags=["CBT Practice"])
class PracticeController:

    @route.get("/available-tests", response=List[StudentsTestListingSchema])
    def get_available_tests(
        self, year_id: Optional[int] = None, test_type_id: Optional[int] = None
    ):
        """Get all available tests for practice in a summarized format"""
        tests = Test.objects.select_related("testYear", "texttype").prefetch_related(
            "testSubject"
        )

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
                subject_questions = list(subject.questions.prefetch_related("answers").all())
                marks = (
                    subject.questions.aggregate(total=Sum("questionMark"))[
                        "total"] or 0
                )

                subjects.append(
                    {
                        "id": subject.id,
                        "subjectname": subject.subjectname,
                        "subjectduration": subject.subjectduration,
                        "questions_count": question_count,
                        "questions": subject_questions,
                    }
                )

                total_questions += question_count
                total_marks += marks
                total_duration += subject.subjectduration

            test_list.append(
                {
                    "test_id": test.pk,
                    "test_name": f"{test.testYear.year if test.testYear else ''} {test.texttype.testtype if test.texttype else ''} Test",
                    "subjects": subjects,
                    "total_questions": total_questions,
                    "total_marks": total_marks,
                    "duration": total_duration,
                }
            )

        return test_list

    @route.post(
        "/start-test", response=StudentsTestListingSchema, auth=JWTAuth()
    )
    def start_test(self, payload: StudentTestRequestSchema):
        """Start a practice test for a student for the subjects he selected"""
        test = get_object_or_404(Test, id=payload.test_id)

        # Get all questions for the test
        subjects = []
        total_duration = 0
        total_questions = 0
        total_marks = 0

        filter_subjects = payload.subject_ids or []
        for subject in test.testSubject.all():
            if filter_subjects and subject.id not in filter_subjects:
                continue
            
            # Get questions with their answers for this subject
            subject_questions = list(subject.questions.prefetch_related("answers").all())
            question_count = len(subject_questions)
            subject_marks = sum(q.questionMark for q in subject_questions)
            
            subjects.append({
                "id": subject.id,
                "subjectname": subject.subjectname,
                "subjectduration": subject.subjectduration,
                "questions_count": question_count,
                "questions": subject_questions,
            })
            
            total_questions += question_count
            total_marks += subject_marks
            total_duration += subject.subjectduration

        return {
            "test_id": test.pk,
            "test_name": f"{test.testYear.year if test.testYear else ''} {test.texttype.testtype if test.texttype else ''} Test",
            "subjects": subjects,
            "total_questions": total_questions,
            "total_marks": total_marks,
            "duration": total_duration,
        }

    @route.post(
        "/submit-test", response=TestResultSchema, auth=JWTAuth()
    )
    def submit_test(self, request, payload: TestSubmissionSchema):
        """Submit test answers and calculate score"""

        test = get_object_or_404(Test, id=payload.student_test_id)

        # Create a new test result instance
        test_result = TestResult.objects.create(
            user=request.user,
            test=test,
            organization=None,  # For practice tests
            mark=0,
        )

        submission_details = {}
        total_score = 0

        for question_answer in payload.questions:
            question = get_object_or_404(
                Question, id=question_answer.question_id)

            # Get subject (assuming M2M between Question and Subject)
            subject = question.subject_set.first()  # type: ignore
            subject_name = subject.subjectname if subject else "Unknown"

            if subject_name not in submission_details:
                submission_details[subject_name] = {
                    "subject_name": subject_name,
                    "selected_answers": [],
                    "subject_score": 0,
                }

            if question_answer.selected_answer_id:
                selected_answer = get_object_or_404(
                    Answer, id=question_answer.selected_answer_id
                )
                submission_details[subject_name]["selected_answers"].append(
                    selected_answer.pk)

                if selected_answer.isCorrect:
                    submission_details[subject_name]["subject_score"] += question.questionMark
                    total_score += question.questionMark

        # Update test result
        test_result.mark = total_score
        test_result.test_submission_details = list(submission_details.values())
        test_result.save()

        return test_result

    @route.get(
        "/my-results",
        response=List[TestResultSchema],
        auth=JWTAuth(),
    )
    def get_my_test_results(self, request):
        """Get all test results for the current user"""
        test_results = TestResult.objects.filter(user=request.user).prefetch_related(
            "tests"
        )
        return test_results

    @route.get(
        "/result/{result_id}", response=TestResultSchema, auth=JWTAuth()
    )
    def get_test_result(self, request, result_id: int):
        """Get detailed test result"""
        test_result = get_object_or_404(
            TestResult.objects.prefetch_related(
                "tests__testSubject__questions__answers"
            ),
            id=result_id,
            user=request.user,
        )
        return test_result
