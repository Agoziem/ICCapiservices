from rest_framework import serializers
from .models import *
from utils import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        ref_name = "ProductCategory"
        
class CreateCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category']
        ref_name = "ProductCreateCategory"

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    
    class Meta:
        model = SubCategory
        fields = '__all__'
        ref_name = "ProductSubCategory"
        
class CreateSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['subcategory', 'category']
        ref_name = "ProductCreateSubCategory"

class ProductSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)


    class Meta:
        model = Product
        fields = '__all__'  # Include all fields from the Product model
        extra_kwargs = {
            'preview': {'allow_null': True, 'required': False},
            'product': {'allow_null': True, 'required': False},
        }
        ref_name = "ProductSerializer"

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
    
class PaginatedProductSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True, required=False)
    previous = serializers.URLField(allow_null=True, required=False)
    results = ProductSerializer(many=True)
    
    class Meta:
        ref_name = "PaginatedProductSerializer"


class CreateProductSerializer(serializers.ModelSerializer):
    preview = serializers.ImageField(allow_null=True, required=False)
    product = serializers.FileField(allow_null=True, required=False)
    category = serializers.IntegerField()
    subcategory = serializers.IntegerField()
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'preview', 'product',
            'category', 'subcategory', 'organization'
        ]
        ref_name = "CreateProductSerializer"


class UpdateProductSerializer(serializers.ModelSerializer):
    preview = serializers.ImageField(allow_null=True, required=False)
    product = serializers.FileField(allow_null=True, required=False)
    category = serializers.IntegerField()
    subcategory = serializers.IntegerField()
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'preview', 'product',
            'category', 'subcategory'
        ]
        ref_name = "UpdateProductSerializer"

