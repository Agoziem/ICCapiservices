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
    answers = AnswerSerializer(many=True)
    class Meta:
        model = Question
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    class Meta:
        model = Subject
        fields = '__all__'

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])  # Use an empty list if questions are missing

        subject = Subject.objects.create(**validated_data)

        for question_data in questions_data:
            question, created = Question.objects.get_or_create(**question_data)
            subject.questions.add(question)

        return subject

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions', [])  # Use an empty list if questions are missing
        instance.subjectname = validated_data.get('subjectname', instance.subjectname)
        instance.subjectduration = validated_data.get('subjectduration', instance.subjectduration)
        instance.save()

        if questions_data:  # Only update questions if provided
            instance.questions.clear()
            for question_data in questions_data:
                question, created = Question.objects.get_or_create(**question_data)
                instance.questions.add(question)

        return instance


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

