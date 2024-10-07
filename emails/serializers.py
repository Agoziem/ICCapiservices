from rest_framework import serializers
from .models import *

class EmailSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Custom date-time format
    class Meta:
        model = Email
        fields = '__all__'

class EmailMessageSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Custom date-time format
    class Meta:
        model = EmailMessage
        fields = '__all__'

class EmailResponseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  # Custom date-time format
    class Meta:
        model = EmailResponse
        fields = '__all__'