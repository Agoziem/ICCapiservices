from django.contrib import admin

from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'message', 'viewed']
    search_fields = ['title', 'message']
    list_filter = ['viewed', 'created_at', 'updated_at']
    list_display_links = ['title']
    list_editable = ['viewed']
