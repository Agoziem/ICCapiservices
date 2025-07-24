from django.contrib import admin
from .models import *

@admin.register(Year)
class YearsAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)
    list_filter = ('year',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subjectname',"subjectduration")
    search_fields = ('subjectname',"subjectduration")
    list_filter = ('subjectname',"subjectduration")

@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    list_display = ('testtype',)
    search_fields = ('testtype',)
    list_filter = ('testtype',)

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('answertext',)
    search_fields = ('answertext',)

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
    list_display = ('testYear','texttype','testorganization')
    list_filter = ('testYear','texttype','testorganization')
    search_fields = ('testYear','texttype','testorganization')

@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    list_display = ('user','mark','date')
    list_filter = ('user','date')
    search_fields = ('user','mark')
    sortable_by = ('user','mark','date')
