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

class ProductSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    preview = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    product = serializers.FileField(allow_null=True, required=False)
    product_url = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    category = CategorySerializer()
    
    class Meta:
        model = Product
        fields = '__all__'

    def get_organization(self, obj):
        return {'id': obj.organization.id, 'name': obj.organization.name}
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.preview)
    
    def get_img_name(self, obj):
        return get_image_name(obj.preview)
    
    def get_product_url(self, obj):
        return get_full_image_url(obj.product)
    
    def get_product_name(self, obj):
        return get_image_name(obj.product)
