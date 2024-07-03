from django.contrib import admin
from .models import Whatsappuser

# Register your models here.
@admin.register(Whatsappuser)
class WhatsappuserAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at', 'updated_at')
    search_fields = ('name', 'phone')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)