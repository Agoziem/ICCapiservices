from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["title", "message" ]
    search_fields = ["title", "message"]
    list_filter = ["created_at", "updated_at"]
    list_display_links = ["title"]
