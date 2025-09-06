from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import Question, Answer, Subject
from ..serializers import CreateQuestionSerializer, QuestionSerializer, AnswerSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(method="post", request_body=CreateQuestionSerializer, responses={201: QuestionSerializer, 400: 'Bad Request', 404: 'Subject Not Found'})
@api_view(['POST'])
def create_question(request, subject_id):
    # Validate input data using serializer
    serializer = CreateQuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        subject = Subject.objects.get(id=subject_id)
        
        questiontext = validated_data.get('questiontext')
        questionMark = validated_data.get('questionMark', 0)
        correctAnswerdescription = validated_data.get('correctAnswerdescription', '')
        
        # Check if question already exists
        existing_question = Question.objects.filter(
            questiontext=questiontext,
            questionMark=questionMark,
            correctAnswerdescription=correctAnswerdescription
        ).first()
        
        if existing_question:
            return Response({'error': 'Question already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create new question
        question = Question.objects.create(
            questiontext=questiontext,
            questionMark=questionMark,
            correctAnswerdescription=correctAnswerdescription
        )
        
        # Add answers to the question
        for answer_data in validated_data.get('answers', []):
            answertext = answer_data.get('answertext')
            isCorrect = answer_data.get('isCorrect', False)
            answer, _ = Answer.objects.get_or_create(answertext=answertext, isCorrect=isCorrect)
            question.answers.add(answer)
        
        question.save()
        subject.questions.add(question)
        
        question_serializer = QuestionSerializer(question)
        return Response(question_serializer.data, status=status.HTTP_201_CREATED)

    except Subject.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error creating question: {str(e)}")
        return Response({'error': 'An error occurred during question creation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Update Question View
@swagger_auto_schema(method="put", request_body=CreateQuestionSerializer, responses={200: QuestionSerializer, 404: 'Question Not Found'})
@api_view(['PUT'])
def update_question(request, question_id):
    # Validate input data using serializer
    serializer = CreateQuestionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    validated_data = serializer.validated_data
    
    try:
        question = Question.objects.get(id=question_id)
        
        # Update question fields
        question.questiontext = validated_data.get('questiontext', question.questiontext)
        question.questionMark = validated_data.get('questionMark', question.questionMark)
        question.correctAnswerdescription = validated_data.get('correctAnswerdescription', question.correctAnswerdescription)
        
        # Clear existing answers and add new ones
        question.answers.clear()
        question.save()
        
        for answer_data in validated_data.get('answers', []):
            answertext = answer_data.get('answertext')
            isCorrect = answer_data.get('isCorrect', False)
            answer, created = Answer.objects.get_or_create(
                answertext=answertext, 
                isCorrect=isCorrect
            )
            question.answers.add(answer)
        
        question.save()
        question_serializer = QuestionSerializer(question)
        return Response(question_serializer.data, status=status.HTTP_200_OK)
        
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error updating question: {str(e)}")
        return Response({'error': 'An error occurred during question update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(method="delete", responses={204: 'Question deleted successfully', 404: 'Question Not Found'})
@api_view(['DELETE'])
def delete_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return Response({'message': 'Question deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error deleting question: {str(e)}")
        return Response({'error': 'An error occurred during question deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

