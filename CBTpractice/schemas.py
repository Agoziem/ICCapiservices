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
    answers: List[AnswerSchema]

    class Meta:
        model = Question
        fields = "__all__"


class SubjectSchema(ModelSchema):
    questions: List[QuestionSchema]

    class Meta:
        model = Subject
        fields = "__all__"


class TestSchema(ModelSchema):
    testYear: Optional[YearSchema] = None
    texttype: Optional[TestTypeSchema] = None
    testSubject: List[SubjectSchema]

    class Meta:
        model = Test
        fields = "__all__"

class TestMiniSchema(Schema):
    id: int
    testYear: Optional[YearSchema] = None
    texttype: Optional[TestTypeSchema] = None
    subjects_count: int = 0

class TestSubmissionDetailSchema(Schema):
    subject_name: str
    selected_answers: List[int]
    subject_score: int = 0

class TestResultSchema(ModelSchema):
    test_submission_details: List[TestSubmissionDetailSchema]

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
    answers: List[CreateAnswerSchema]


class UpdateQuestionSchema(Schema):
    questiontext: Optional[str] = None
    questionMark: Optional[int] = None
    required: Optional[bool] = None
    correctAnswerdescription: Optional[str] = None
    answers: List[CreateAnswerSchema]


class CreateSubjectSchema(Schema):
    subjectname: str
    subjectduration: int = 0
    # questions: List[CreateQuestionSchema]


class UpdateSubjectSchema(Schema):
    subjectname: Optional[str] = None
    subjectduration: Optional[int] = None
    # questions: List[UpdateQuestionSchema]


class CreateTestSchema(Schema):
    testYear: int
    texttype: int
    testorganization: Optional[int] = None
    # testSubject: List[int]


class UpdateTestSchema(Schema):
    testYear: Optional[int] = None
    texttype: Optional[int] = None
    # testSubject: List[int]


# Student Test Schemas
class StudentTestRequestSchema(Schema):
    user_id: int
    test_id: int
    subject_ids: List[int]


class QuestionAnswerSchema(Schema):
    question_id: int
    selected_answer_id: Optional[int] = None


class TestSubmissionSchema(Schema):
    student_test_id: int
    questions: List[QuestionAnswerSchema]



# Response Schemas
class ErrorResponseSchema(Schema):
    error: str


class SuccessResponseSchema(Schema):
    message: str


# Paginated response schemas
class PaginatedTestResponseSchema(Schema):
    count: int
    items: List[TestSchema]


class PaginatedSubjectResponseSchema(Schema):
    count: int
    items: List[SubjectSchema]


class PaginatedQuestionResponseSchema(Schema):
    count: int
    items: List[QuestionSchema]


class PaginatedTestResultResponseSchema(Schema):
    count: int
    items: List[TestResultSchema]


class SubjectSummarySchema(Schema):
    id: int
    subjectname: str
    subjectduration: int
    questions_count: int = 0
    questions: List[QuestionSchema]

# Practice/Student specific schemas
class StudentsTestListingSchema(Schema):
    test_id: int
    test_name: str
    subjects: Optional[List[SubjectSummarySchema]] = None
    total_questions: int = 0
    total_marks: int = 0
    duration: int = 0

