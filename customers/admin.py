from django.contrib import admin
from .models import *


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "date_created")
    search_fields = ("name", "email", "phone")
    list_filter = ("date_created",)
    sortable_by = ("name", "email", "phone", "date_created")
