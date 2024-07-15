from django.contrib import admin
from .models import Video, Category

# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'organization', 'category', 'created_at', 'updated_at']
    list_filter = ['organization', 'category']
    search_fields = ['title', 'organization', 'category']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    list_filter = ['name']
    search_fields = ['name']