from typing import Optional, List
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Year, TestType, Answer, Question, Subject, Test, TestResult


# Base Model Schemas
class YearSchema(ModelSchema):
    class Meta:
        model = Year
        fields = "__all__"


class TestTypeSchema(ModelSchema):
    class Meta:
        model = TestType
        fields = "__all__"


class AnswerSchema(ModelSchema):
    class Meta:
        model = Answer
        fields = "__all__"


class QuestionSchema(ModelSchema):
    answers: List[AnswerSchema] = []

    class Meta:
        model = Question
        fields = "__all__"


class SubjectSchema(ModelSchema):
    questions: List[QuestionSchema] = []

    class Meta:
        model = Subject
        fields = "__all__"


class TestSchema(ModelSchema):
    testYear: Optional[YearSchema] = None
    texttype: Optional[TestTypeSchema] = None
    testSubject: List[SubjectSchema] = []

    class Meta:
        model = Test
        fields = "__all__"


class TestResultSchema(ModelSchema):
    tests: List[TestSchema] = []

    class Meta:
        model = TestResult
        fields = "__all__"


# Input Schemas for Creating/Updating
class CreateYearSchema(Schema):
    year: int


class UpdateYearSchema(Schema):
    year: Optional[int] = None


class CreateTestTypeSchema(Schema):
    testtype: str


class UpdateTestTypeSchema(Schema):
    testtype: Optional[str] = None


class CreateAnswerSchema(Schema):
    answertext: str
    isCorrect: bool = False


class UpdateAnswerSchema(Schema):
    answertext: Optional[str] = None
    isCorrect: Optional[bool] = None


class CreateQuestionSchema(Schema):
    questiontext: str
    questionMark: int = 0
    required: bool = True
    correctAnswerdescription: Optional[str] = None
    answers: List[CreateAnswerSchema] = []


class UpdateQuestionSchema(Schema):
    questiontext: Optional[str] = None
    questionMark: Optional[int] = None
    required: Optional[bool] = None
    correctAnswerdescription: Optional[str] = None
    answers: Optional[List[CreateAnswerSchema]] = None


class CreateSubjectSchema(Schema):
    subjectname: str
    subjectduration: int = 0
    questions: Optional[List[dict]] = []


class UpdateSubjectSchema(Schema):
    subjectname: Optional[str] = None
    subjectduration: Optional[int] = None
    questions: Optional[List[dict]] = None


class CreateTestSchema(Schema):
    testYear: int
    texttype: int
    testSubject: List[int]
    testorganization: Optional[int] = None


class UpdateTestSchema(Schema):
    testYear: Optional[int] = None
    texttype: Optional[int] = None
    testSubject: Optional[List[int]] = None


# Student Test Schemas
class StudentTestRequestSchema(Schema):
    user_id: int
    test_id: int
    examSubjects: List[dict] = []


class QuestionAnswerSchema(Schema):
    question_id: int
    selected_answer_id: Optional[int] = None


class TestSubmissionSchema(Schema):
    student_test_id: int
    questions: List[QuestionAnswerSchema]


class SubmitStudentTestSchema(Schema):
    submissions: List[TestSubmissionSchema]


class TestScoreResponseSchema(Schema):
    Total: int
    subject_scores: dict = {}


# Response Schemas
class YearListResponseSchema(Schema):
    years: List[YearSchema] = []


class TestTypeListResponseSchema(Schema):
    testtypes: List[TestTypeSchema] = []


class SubjectListResponseSchema(Schema):
    subjects: List[SubjectSchema] = []


class TestListResponseSchema(Schema):
    tests: List[TestSchema] = []


class TestResultListResponseSchema(Schema):
    test_results: List[TestResultSchema] = []


class ErrorResponseSchema(Schema):
    error: str


class SuccessResponseSchema(Schema):
    message: str


# Simplified schemas for listing without deep nesting
class SubjectSummarySchema(Schema):
    id: int
    subjectname: str
    subjectduration: int
    questions_count: int = 0

    @staticmethod
    def resolve_questions_count(obj):
        return obj.questions.count()


class TestSummarySchema(Schema):
    id: int
    testYear: Optional[YearSchema] = None
    texttype: Optional[TestTypeSchema] = None
    subjects_count: int = 0

    @staticmethod
    def resolve_subjects_count(obj):
        return obj.testSubject.count()


class QuestionSummarySchema(Schema):
    id: int
    questiontext: str
    questionMark: int
    required: bool
    answers_count: int = 0

    @staticmethod
    def resolve_answers_count(obj):
        return obj.answers.count()


# Practice/Student specific schemas
class StudentTestSchema(Schema):
    test_id: int
    test_name: str
    subjects: List[SubjectSummarySchema] = []
    total_questions: int = 0
    total_marks: int = 0
    duration: int = 0


class StudentTestDetailSchema(Schema):
    test: TestSchema
    questions: List[QuestionSchema] = []
    total_questions: int
    total_marks: int
    time_limit: int
