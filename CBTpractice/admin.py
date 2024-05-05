from django.contrib import admin
from .models import *

@admin.register(Year)
class YearsAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)
    list_filter = ('year',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subjectname',)
    search_fields = ('subjectname',)
    list_filter = ('subjectname',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answertext','isCorrect')
    search_fields = ('answertext',)
    list_filter = ('isCorrect',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('truncated_questiontext','questionMark','required')
    search_fields = ('questiontext',)
    list_filter = ('required',)

    def truncated_questiontext(self, obj):
        question_lenght = 50
        if len(obj.questiontext) > question_lenght:
            return obj.questiontext[:question_lenght] + '...'
        else:
            return obj.questiontext


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('testSubject','testYear','testTime','testMark')
    list_filter = ('testSubject','testYear')
    search_fields = ('testSubject','testYear')

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user','mark','date')
    list_filter = ('user','date')
    search_fields = ('user','mark')
    sortable_by = ('user','mark','date')
