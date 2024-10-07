from django.contrib import admin
from .models import *

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_filter = ('created_at',)
    sortable_by = ('name', 'email', 'subject', 'created_at')

@admin.register(EmailResponse)
class EmailResponseAdmin(admin.ModelAdmin):
    list_display = ('recipient_email', 'response_subject', 'created_at')
    search_fields = ('email', 'subject')
    list_filter = ('created_at',)
    sortable_by = ('recipient_email', 'response_subject', 'created_at')

@admin.register(EmailMessage)
class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at')
    search_fields = ('subject',)
    list_filter = ('created_at',)
    sortable_by = ('subject', 'created_at')