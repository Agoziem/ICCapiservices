from rest_framework import serializers
from .models import *
import re

class ProductSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_image(self, obj):
        Image = obj.image
        if not Image:
            return None 
        
        Image_url = Image.url
        if not Image_url.startswith(('http://', 'https://')):
            image_url = f"http://127.0.0.1:8000{Image_url}"  
        pattern_media = r'^/media/'
        pattern_percent_3A = r'%3A'
        modified_url = re.sub(pattern_media, '', image_url)
        modified_url = re.sub(pattern_percent_3A, ':/', modified_url, count=1)
        modified_url = re.sub(pattern_percent_3A, ':', modified_url)
        return modified_url