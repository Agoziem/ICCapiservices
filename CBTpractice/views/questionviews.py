from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Question, Answer, Subject
from ..serializers import QuestionSerializer, AnswerSerializer


@api_view(['POST'])
def create_question(request, subject_id):
    data = request.data
    correct_answer = None
    try:
        subject = Subject.objects.get(id=subject_id)
        questiontext = data.get('questiontext', None)
        questionMark = data.get('questionMark', 0)
        correctAnswerdescription = data.get('correctAnswerdescription', None)
        question, created = Question.objects.get_or_create(
            questiontext=questiontext,
            questionMark=questionMark,
            correctAnswerdescription=correctAnswerdescription
        )
        if created:
            for answer_data in data.get('answers', []):
                answertext = answer_data.get('answertext', None)
                isCorrect = answer_data.get('isCorrect', False)
                answer, _ = Answer.objects.get_or_create(answertext=answertext)
                question.answers.add(answer)
                if isCorrect:
                    correct_answer = answer

            if correct_answer:
                question.correctAnswer = correct_answer
            question.save()
            subject.questions.add(question)
            question_serializer = QuestionSerializer(question)
            return Response(question_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Question already exists'}, status=status.HTTP_400_BAD_REQUEST)

    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Update Question View
@api_view(['PUT'])
def update_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        data = request.data
        correctanswer = ""
        questiontext = data.get('questiontext', question.questiontext)
        questionMark = data.get('questionMark', question.questionMark)
        correctAnswerdescription = data.get('correctAnswerdescription', question.correctAnswerdescription)
        question.questiontext = questiontext
        question.questionMark = questionMark
        question.correctAnswerdescription = correctAnswerdescription
        question.answers.clear()
        question.save()
        for answer in data.get('answers', question.answers.all()):
            answertext = answer.get('answertext', None)
            isCorrect = answer.get('isCorrect', False)
            answer,created = Answer.objects.get_or_create(answertext=answertext)
            question.answers.add(answer)
            if isCorrect:
                correctanswer = answer
        question.correctAnswer = correctanswer
        question.save()
        question_serializer = QuestionSerializer(question)
        return Response(question_serializer.data, status=status.HTTP_200_OK)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Answer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Question.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# Create Question View
# //   {
# //     "id": 8,
# //     "answers": [
# //         {
# //             "id": 14,
# //             "answertext": "True"
# //         },
# //         {
# //             "id": 15,
# //             "answertext": "False"
# //         }
# //     ],
# //     "correctAnswer": null,
# //     "questiontext": "The Lord is Good",
# //     "questionMark": 2,
# //     "required": true,
# //     "correctAnswerdescription": "The Lord is indeed Good"
# // } from the database

# // {
# //   id: "",
# //   questiontext: "",
# //   questionMark: "",
# //   answers: [
# //     {
# //       answertext: "",
# //       isCorrect: false,
# //     },
# //   ],
# //   correctAnswerdescription: "",
# // } for the form