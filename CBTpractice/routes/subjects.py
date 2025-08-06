from typing import List
from ninja import Query
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Count
from ninja_jwt.authentication import JWTAuth

from ..models import Subject, Question, Answer, Test
from ..schemas import (
    SubjectSchema,
    CreateSubjectSchema,
    UpdateSubjectSchema,
    QuestionSchema,
    CreateQuestionSchema,
    UpdateQuestionSchema,
    AnswerSchema,
    CreateAnswerSchema,
    UpdateAnswerSchema,
    SuccessResponseSchema,
)


@api_controller("/subjects", tags=["CBT Subjects"])
class SubjectsController:

    @route.get("/test_id/{test_id}", response=List[SubjectSchema])
    def list_subjects(self, test_id: int, include_questions: bool = False):
        """Get all subjects with optional questions"""
        test = get_object_or_404(Test, id=test_id)
        
        if include_questions:
            subjects = Subject.objects.prefetch_related("questions__answers").filter(tests=test)
        else:
            subjects = Subject.objects.annotate(
                questions_count=Count("questions")
            ).filter(tests=test)

        return subjects


    @route.post("/test_id/{test_id}", response=SubjectSchema, auth=JWTAuth())
    def create_subject(self, test_id: int, payload: CreateSubjectSchema):
        """Create a new subject"""
        subject_data = payload.model_dump()
        subject = Subject.objects.create(**subject_data)
        test = get_object_or_404(Test, id=test_id)
        test.testSubject.add(subject)
        return subject

    @route.get("/subject_id/{subject_id}", response=SubjectSchema)
    def get_subject(self, subject_id: int):
        """Get a specific subject with all questions and answers"""
        subject = get_object_or_404(
            Subject.objects.prefetch_related("questions__answers"), id=subject_id
        )
        return subject

    @route.put("/subject_id/{subject_id}", response=SubjectSchema, auth=JWTAuth())
    def update_subject(self, subject_id: int, payload: UpdateSubjectSchema):
        """Update a subject"""
        subject = get_object_or_404(Subject, id=subject_id)

        subject_data = payload.model_dump(exclude_unset=True)
        for attr, value in subject_data.items():
            setattr(subject, attr, value)
        subject.save()

        return subject

    @route.delete(
        "/subject_id/{subject_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_subject(self, subject_id: int):
        """Delete a subject"""
        subject = get_object_or_404(Subject, id=subject_id)
        subject.delete()
        return {"message": "Subject deleted successfully"}

    @route.get("/subject_id/{subject_id}/questions", response=List[QuestionSchema])
    def list_subject_questions(self, subject_id: int):
        """Get all questions for a specific subject"""
        subject = get_object_or_404(Subject, id=subject_id)
        questions = subject.questions.prefetch_related("answers").all()
        return questions


@api_controller("/questions", tags=["CBT Questions"])
class QuestionsController:

    @route.get("/subject_id/{subject_id}", response=List[QuestionSchema])
    def list_questions(self, subject_id: int):
        """Get all questions with optional subject filtering"""
        subject = get_object_or_404(Subject, id=subject_id)
        questions = subject.questions.prefetch_related("answers").all()
        return questions

    @route.post("/subject_id/{subject_id}", response=QuestionSchema, auth=JWTAuth())
    def create_question(self, subject_id: int, payload: CreateQuestionSchema):
        """Create a new question with answers"""
        question_data = payload.model_dump()
        answers_data = question_data.pop("answers", [])

        question = Question.objects.create(**question_data)
        # Create answers
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
            
        # get the subject
        subject = get_object_or_404(Subject, id=subject_id)
        subject.questions.add(question)
        return question

    @route.get("/question_id/{question_id}", response=QuestionSchema)
    def get_question(self, question_id: int):
        """Get a specific question with all answers"""
        question = get_object_or_404(
            Question.objects.prefetch_related("answers"), id=question_id
        )
        return question

    @route.put("/question_id/{question_id}", response=QuestionSchema, auth=JWTAuth())
    def update_question(self, question_id: int, payload: UpdateQuestionSchema):
        """Update a question"""
        question = get_object_or_404(Question, id=question_id)

        question_data = payload.model_dump(exclude_unset=True)
        answers_data = question_data.pop("answers", None)

        for attr, value in question_data.items():
            setattr(question, attr, value)
        question.save()

        # Handle answers update if provided
        if answers_data is not None:
            # Clear existing answers
            question.answers.all().delete()

            # Create new answers
            for answer_data in answers_data:
                Answer.objects.create(question=question, **answer_data)

        return question

    @route.delete(
        "/question_id/{question_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_question(self, question_id: int):
        """Delete a question"""
        question = get_object_or_404(Question, id=question_id)
        question.delete()
        return {"message": "Question deleted successfully"}

    @route.post(
        "/question_id/{question_id}/answers", response=AnswerSchema, auth=JWTAuth()
    )
    def add_answer(self, question_id: int, payload: CreateAnswerSchema):
        """Add an answer to a question"""
        question = get_object_or_404(Question, id=question_id)
        answer = Answer.objects.create(
            question=question, **payload.model_dump())
        return answer


@api_controller("/answers", tags=["CBT Answers"])
class AnswersController:

    @route.get("/{answer_id}", response=AnswerSchema)
    def get_answer(self, answer_id: int):
        """Get a specific answer"""
        answer = get_object_or_404(Answer, id=answer_id)
        return answer

    @route.put("/{answer_id}", response=AnswerSchema, auth=JWTAuth())
    def update_answer(self, answer_id: int, payload: UpdateAnswerSchema):
        """Update an answer"""
        answer = get_object_or_404(Answer, id=answer_id)

        for attr, value in payload.model_dump(exclude_unset=True).items():
            setattr(answer, attr, value)
        answer.save()

        return answer

    @route.delete(
        "/{answer_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_answer(self, answer_id: int):
        """Delete an answer"""
        answer = get_object_or_404(Answer, id=answer_id)
        answer.delete()
        return {"message": "Answer deleted successfully"}
