from django.contrib import admin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = [
        "email",
        "username",
        "is_staff",
        "is_active",
        "isOauth",
        "Oauthprovider",
    ]
    search_fields = ["email", "username", "last_name"]
    list_filter = ["is_staff", "is_active", "isOauth", "Oauthprovider"]
    ordering = ["email"]
