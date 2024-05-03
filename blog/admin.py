from django.contrib import admin

from .models import *

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'author')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'author')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'created_at')
    search_fields = ('user', 'blog')
    list_filter = ('created_at', 'user')
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'user', 'created_at')
    search_fields = ('content',)
    list_filter = ('created_at', 'user')

