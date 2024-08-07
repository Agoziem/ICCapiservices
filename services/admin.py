from django.contrib import admin
from .models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    search_fields = ('category',)
    sortable_by = ('category',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortened_description', 'price', 'category')
    search_fields = ('name', 'description', 'price')
    list_filter = ('price',)
    sortable_by = ('name', 'price')

    def shortened_description(self, obj):
        description_length = 50
        if len(obj.description) > description_length:
            return obj.description[:description_length] + '...'
        else:
            return obj.description
        
@admin.register(SubCategory)
class SubCategory(admin.ModelAdmin):
    list_display = ['category', 'subcategory']
    list_filter = ['category']
    search_fields = ['category', 'subcategory']
