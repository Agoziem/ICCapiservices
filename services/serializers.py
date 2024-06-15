from rest_framework import serializers
from .models import *
from utils import *

class ServiceSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    preview = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    class Meta:
        model = Service
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.preview)
    
    def get_img_name(self, obj):
        return get_image_name(obj.preview)

        
    