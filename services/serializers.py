from rest_framework import serializers
from .models import *
import re

class ServiceSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    

    def get_preview(self, obj):
        preview = obj.preview
        if not preview:
            return None 
        
        preview_url = preview.url
        if not preview_url.startswith(('http://', 'https://')):
            Preview_url = f"http://127.0.0.1:8000{preview_url}"  
        pattern_media = r'^/media/'
        pattern_percent_3A = r'%3A'
        modified_url = re.sub(pattern_media, '', Preview_url)
        modified_url = re.sub(pattern_percent_3A, ':/', modified_url, count=1)
        modified_url = re.sub(pattern_percent_3A, ':', modified_url)
        return modified_url
    