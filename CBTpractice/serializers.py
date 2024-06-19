from rest_framework import serializers
from .models import *

class YearsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Year
        fields = '__all__'

class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, required=False)
    correctAnswer = AnswerSerializer(required=False)

    class Meta:
        model = Question
        fields = '__all__'
    
class SubjectSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Subject
        fields = '__all__'
        extra_kwargs = {'questions': {'required': False}}


class TestSerializer(serializers.ModelSerializer):
    testYear = YearsSerializer(many=False)
    texttype = TestTypeSerializer(many=False)
    testSubject = SubjectSerializer(many=True)
    class Meta:
        model = Test
        fields = '__all__'

class TestResultSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True)
    class Meta:
        model = TestResult
        fields = '__all__'

