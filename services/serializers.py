from rest_framework import serializers

from ICCapp.serializers import OrganizationMiniSerializer
from .models import *
from utils import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        ref_name = "ServiceCategory"
        
class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
        ref_name = "ServiceCreateCategory"

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = SubCategory
        fields = '__all__'
        ref_name = "ServiceSubCategory"
        
class CreateSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['subcategory', 'category']
        ref_name = "ServiceCreateSubCategory"
# 
class ServiceSerializer(serializers.ModelSerializer):
    organization = OrganizationMiniSerializer(read_only=True)
    preview = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = '__all__'
        ref_name = "ServiceSerializer"
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.preview)
    
    def get_img_name(self, obj):
        return get_image_name(obj.preview)

class PaginatedServiceSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = ServiceSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedServiceSerializer"
        fields = ['count', 'next', 'previous', 'results']

class CreateServiceSerializer(serializers.ModelSerializer):
    preview = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'preview', 'category', 'subcategory', 'organization']
        ref_name = "CreateServiceSerializer"
        
class UpdateServiceSerializer(serializers.ModelSerializer):
    preview = serializers.ImageField(allow_null=True, required=False)
    
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'preview', 'category', 'subcategory']
        ref_name = "UpdateServiceSerializer"
    



        
    