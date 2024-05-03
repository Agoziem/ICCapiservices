from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

# Years model
class Years(models.Model):
    year = models.IntegerField(default=2021,blank=False)
    
    def __str__(self):
        return str(self.year)

# Subject model
class Subject(models.Model):
    subjectname = models.CharField(max_length=255,default="None",blank=False)
    
    def __str__(self):
        return str(self.subjectname)

# Answer model
class Answer(models.Model):
    answertext = models.CharField(max_length=255,default="None",blank=False)
    isCorrect = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.answertext}"

# Question model   
class Question(models.Model):
    questiontext = RichTextField(default="None",blank=False,null=True)
    questionMark = models.IntegerField(default=0,blank=True)
    required=models.BooleanField(default=True)
    answers = models.ManyToManyField(Answer)

    def __str__(self):
        return str(self.questiontext)
    
    class Meta:
        ordering = ['id']

# Test model
class Test(models.Model):
    testSubject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    testYear = models.ForeignKey(Years, on_delete=models.CASCADE)
    testTime = models.IntegerField(default=0,blank=True)
    testMark = models.IntegerField(default=0,blank=True)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return f"{self.testSubject} - {self.testYear}"
    
    class Meta:
        ordering = ['id']


# Test Result model
class TestResult(models.Model):
    tests = models.ManyToManyField(Test)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mark = models.IntegerField(default=0,blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.mark}"
    
    class Meta:
        ordering = ['id']