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
    correctAnswerdescription = serializers.CharField(required=False, allow_blank=True)

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


# --------------------------------------------
# Serializers for creating objects
# --------------------------------------------
class AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answertext', 'isCorrect']  # or all fields you expect during creation

class CreateQuestionSerializer(serializers.ModelSerializer):
    answers = AnswerCreateSerializer(many=True)
    correctAnswerdescription = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Question
        fields = ['questiontext', 'questionMark', 'correctAnswerdescription', 'answers']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers', [])
        question = Question.objects.create(**validated_data)

        for ans_data in answers_data:
            Answer.objects.create(question=question, **ans_data)

        return question


class CreateSubjectSerializer(serializers.ModelSerializer):
    questions = serializers.ListField(
        child=serializers.DictField(), required=False, allow_empty=True
    )
    
    class Meta:
        model = Subject
        fields = ['subjectname', 'subjectduration', 'questions']


class StudentTestRequestSerializer(serializers.Serializer):
    """ 
    Serializer for student test request
    """
    user_id = serializers.IntegerField()
    test_id = serializers.IntegerField()
    examSubjects = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()),
        allow_empty=True
    )


class QuestionAnswerSerializer(serializers.Serializer):
    """ 
    Serializer for question answers in student test submission
    """
    question_id = serializers.IntegerField()

class CreateTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['testYear', 'texttype', 'testSubject']

        extra_kwargs = {
            'testYear': {'required': True},
            'texttype': {'required': True},
            'testSubject': {'required': True}
        }

        def create(self, validated_data):
            test = Test.objects.create(**validated_data)
            return test


class TestSubmissionSerializer(serializers.Serializer):
    student_test_id = serializers.IntegerField()
    questions = QuestionAnswerSerializer(many=True)

class SubmitStudentTestSerializer(serializers.ListSerializer):
    child = TestSubmissionSerializer()


class TestScoreResponseSerializer(serializers.Serializer):
    Total = serializers.IntegerField()
    
    def to_representation(self, instance):
        # Dynamic fields for subject scores
        data = super().to_representation(instance)
        # Add any additional subject score fields dynamically
        for key, value in instance.items():
            if key not in data:
                data[key] = value
        return data