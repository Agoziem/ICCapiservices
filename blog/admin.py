from django.contrib import admin

from .models import *

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title','author', 'date')
    search_fields = ('title', 'body')
    list_filter = ('date', 'author')
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'date')
    search_fields = ('comment',)
    list_filter = ('date', 'user')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    search_fields = ('tag',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    search_fields = ('category',)

