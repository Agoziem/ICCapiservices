from rest_framework import serializers
from .models import *
from utils import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = SubCategory
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    thumbnail = serializers.ImageField(allow_null=True, required=False)
    video = serializers.FileField(allow_null=True, required=False)
    video_url = serializers.SerializerMethodField()
    video_name = serializers.SerializerMethodField()
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    
    class Meta:
        model = Video
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.thumbnail)
    
    def get_img_name(self, obj):
        return get_image_name(obj.thumbnail)
    
    def get_video_url(self, obj):
        return get_full_image_url(obj.video)
    
    def get_video_name(self, obj):
        return get_image_name(obj.video)
    


