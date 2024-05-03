from django.contrib import admin
from .models import *

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'last_updated_date')
    list_filter = ('created_at', 'last_updated_date')
    search_fields = ('name', 'email', 'phone')
    ordering = ('created_at', 'last_updated_date')

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('organization', 'first_name', 'last_name', 'email', 'phone', 'created_at', 'last_updated_date')
    list_filter = ('organization', 'created_at', 'last_updated_date')
    search_fields = ('organization__name', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('organization', 'created_at', 'last_updated_date')

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('organization', 'author', 'created_at', 'last_updated_date')
    list_filter = ('organization', 'created_at', 'last_updated_date')
    search_fields = ('organization__name', 'author')
    ordering = ('organization', 'created_at', 'last_updated_date')

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('organization', 'email')
    list_filter = ('organization',)
    search_fields = ('organization__name', 'email')
    ordering = ('organization',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('organization', 'title', 'created_at', 'last_updated_date')
    list_filter = ('organization', 'created_at', 'last_updated_date')
    search_fields = ('organization__name', 'title')
    ordering = ('organization', 'created_at', 'last_updated_date')
