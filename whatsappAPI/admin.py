from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(WhatsAppBusinessAccount)
class WhatsAppBusinessAccountAdmin(admin.ModelAdmin):
    list_display = ('account_id', 'display_phone_number', 'phone_number_id')
    search_fields = ('account_id', 'display_phone_number', 'phone_number_id')
    list_filter = ('account_id', 'display_phone_number', 'phone_number_id')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('wa_id', 'profile_name')
    search_fields = ('wa_id', 'profile_name')
    list_filter = ('wa_id', 'profile_name')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_account', 'contact', 'timestamp', 'text_body', 'message_type')
    search_fields = ('whatsapp_account', 'contact', 'timestamp', 'text_body', 'message_type')
    list_filter = ('whatsapp_account', 'contact', 'timestamp', 'text_body', 'message_type')