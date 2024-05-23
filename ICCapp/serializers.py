from rest_framework import serializers
from .models import *
import re

class OrganizationSerializer(serializers.ModelSerializer):
    Organizationlogo = serializers.SerializerMethodField()
    class Meta:
        model = Organization
        fields = '__all__'
    
    def get_Organizationlogo(self, obj):
        Organizationlogo = obj.logo
        if not Organizationlogo:
            return None 
        
        Organizationlogo_url = Organizationlogo.url
        if not Organizationlogo_url.startswith(('http://', 'https://')):
            Organizationlogo_url = f"http://127.0.0.1:8000{Organizationlogo_url}"  
        pattern_media = r'^/media/'
        pattern_percent_3A = r'%3A'
        modified_url = re.sub(pattern_media, '', Organizationlogo_url)
        modified_url = re.sub(pattern_percent_3A, ':/', modified_url, count=1)
        modified_url = re.sub(pattern_percent_3A, ':', modified_url)
        return modified_url

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'