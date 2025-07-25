from django.db import models
from ckeditor.fields import RichTextField
from django.conf import settings
from ICCapp.models import Organization


# Year model
class Year(models.Model):
    year = models.IntegerField(default=2021, blank=False)

    def __str__(self):
        return str(self.year)


# Test Type model
class TestType(models.Model):
    testtype = models.CharField(max_length=255, default="None", blank=False)

    def __str__(self):
        return str(self.testtype)


# Answer model
class Answer(models.Model):
    answertext = models.CharField(max_length=255, default="None", blank=False)
    isCorrect = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return f"{self.answertext}"


# Question model
class Question(models.Model):
    questiontext = RichTextField(default="None", blank=False, null=True)
    questionMark = models.IntegerField(default=0, blank=True)
    required = models.BooleanField(default=True)
    answers = models.ManyToManyField(Answer)
    correctAnswerdescription = RichTextField(default="None", blank=True, null=True)

    def __str__(self):
        return str(self.questiontext)

    class Meta:
        ordering = ["id"]


# Subject model
class Subject(models.Model):
    subjectduration = models.IntegerField(default=0, blank=True)
    subjectname = models.CharField(max_length=255, default="None", blank=False)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return str(self.subjectname)


# Test model
class Test(models.Model):
    testorganization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    texttype = models.ForeignKey(
        TestType, on_delete=models.CASCADE, null=True, blank=True
    )
    testSubject = models.ManyToManyField(Subject)
    testYear = models.ForeignKey(Year, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.testSubject} - {self.testYear}"

    class Meta:
        ordering = ["id"]


# Test Result model
class TestResult(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, null=True, blank=True
    )
    tests = models.ManyToManyField(Test)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    mark = models.IntegerField(default=0, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.mark}"

    class Meta:
        ordering = ["id"]
