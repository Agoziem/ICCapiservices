from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'quantity', 'digital', 'created_at', 'last_updated_date']
    list_filter = ['digital', 'created_at', 'last_updated_date']
    search_fields = ['name', 'description']
