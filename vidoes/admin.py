from django.contrib import admin
from .models import Video, Category, SubCategory


# Register your models here.
@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ["title", "organization", "category", "created_at", "updated_at"]
    list_filter = ["organization", "category"]
    search_fields = ["title", "organization", "category"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["category", "description"]
    list_filter = ["category"]
    search_fields = ["category"]


@admin.register(SubCategory)
class SubCategory(admin.ModelAdmin):
    list_display = ["category", "subcategory"]
    list_filter = ["category"]
    search_fields = ["category", "subcategory"]
