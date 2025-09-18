from rest_framework import serializers
from .models import NotificationModified as Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'viewed', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']  # These fields are automatically set by Django

