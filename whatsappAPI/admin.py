from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('wa_id', 'profile_name')
    list_filter = ('wa_id', 'profile_name')
    search_fields = ('wa_id', 'profile_name')

@admin.register(ReceivedMessage)
class ReceivedMessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'message_type','message_mode', 'timestamp')
    list_filter = ('contact', 'message_type','message_mode', 'timestamp')
    search_fields = ('contact', 'message_type','message_mode', 'timestamp')

@admin.register(SentMessage)
class SentMessageAdmin(admin.ModelAdmin):
    list_display = ('contact', 'message_type','message_mode', 'timestamp', 'status')
    list_filter = ('contact', 'message_type','message_mode', 'timestamp', 'status')
    search_fields = ('contact', 'message_type','message_mode', 'timestamp', 'status')


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('message', 'status', 'timestamp')
    list_filter = ('message', 'status', 'timestamp')
    search_fields = ('message', 'status', 'timestamp')

@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'received_at')
    list_filter = ('event_id', 'received_at')
    search_fields = ('event_id', 'received_at')