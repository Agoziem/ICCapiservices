from django.contrib import admin
from .models import Contact, WAMessage, Status, WebhookEvent, WATemplateSchema


# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("wa_id", "profile_name")
    list_filter = ("wa_id", "profile_name")
    search_fields = ("wa_id", "profile_name")


@admin.register(WAMessage)
class WAMessageAdmin(admin.ModelAdmin):
    list_display = ("contact", "message_type", "message_mode", "timestamp")
    list_filter = ("contact", "message_type", "message_mode", "timestamp")
    search_fields = ("contact", "message_type", "message_mode", "timestamp")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ("message", "status", "timestamp")
    list_filter = ("message", "status", "timestamp")
    search_fields = ("message", "status", "timestamp")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "received_at")
    list_filter = ("event_id", "received_at")
    search_fields = ("event_id", "received_at")


@admin.register(WATemplateSchema)
class WATemplateSchemaAdmin(admin.ModelAdmin):
    list_display = ("template", "title", "created_at")
    list_filter = ("template", "created_at")
    search_fields = ("template", "text", "created_at")

    readonly_fields = ("created_at",)

    fieldsets = (
        ("Template Information", {"fields": ("template", "text", "link", "status")}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
