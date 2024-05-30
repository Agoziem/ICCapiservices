from django.contrib import admin
from .models import Orders

@admin.register(Orders)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'status', 'created_at', 'last_updated_date')
    list_filter = ('status', 'created_at', 'last_updated_date')
    search_fields = ('customer__name', 'customer__email', 'amount', 'status')
    ordering = ('status', 'created_at', 'last_updated_date')
