from typing import Optional
from ninja import ModelSchema, Schema, File
from ninja.files import UploadedFile
from datetime import datetime
from decimal import Decimal
from .models import Product, Category, SubCategory


# Base Model Schemas
class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = '__all__'


class SubCategorySchema(ModelSchema):
    category_details: Optional[CategorySchema] = None
    
    class Meta:
        model = SubCategory
        fields = '__all__'
    
    @staticmethod
    def resolve_category_details(obj):
        if obj.category:
            return obj.category
        return None


class ProductSchema(ModelSchema):
    organization_details: Optional[dict] = None
    img_url: Optional[str] = None
    img_name: Optional[str] = None
    product_url: Optional[str] = None
    product_name: Optional[str] = None
    category_details: Optional[CategorySchema] = None
    subcategory_details: Optional[SubCategorySchema] = None
    buyers_count: Optional[int] = None
    
    class Meta:
        model = Product
        fields = '__all__'
    
    @staticmethod
    def resolve_organization_details(obj):
        if obj.organization:
            return {
                'id': obj.organization.id,
                'name': obj.organization.name
            }
        return None
    
    @staticmethod
    def resolve_img_url(obj):
        return obj.preview.url if obj.preview else None
    
    @staticmethod
    def resolve_img_name(obj):
        return obj.preview.name if obj.preview else None
    
    @staticmethod
    def resolve_product_url(obj):
        return obj.product.url if obj.product else None
    
    @staticmethod
    def resolve_product_name(obj):
        return obj.product.name if obj.product else None
    
    @staticmethod
    def resolve_category_details(obj):
        if obj.category:
            return obj.category
        return None
    
    @staticmethod
    def resolve_subcategory_details(obj):
        if obj.subcategory:
            return obj.subcategory
        return None
    
    @staticmethod
    def resolve_buyers_count(obj):
        return obj.userIDs_that_bought_this_product.count()


# Input Schemas for Creating/Updating
class CreateCategorySchema(Schema):
    category: str
    description: Optional[str] = None


class UpdateCategorySchema(Schema):
    category: Optional[str] = None
    description: Optional[str] = None


class CreateSubCategorySchema(Schema):
    subcategory: str
    category: int


class UpdateSubCategorySchema(Schema):
    subcategory: Optional[str] = None
    category: Optional[int] = None


class CreateProductSchema(Schema):
    name: str
    description: str = "No description available"
    price: Decimal
    category: int
    subcategory: Optional[int] = None
    digital: Optional[bool] = True
    free: Optional[bool] = False
    rating: Optional[int] = 0


class UpdateProductSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[int] = None
    subcategory: Optional[int] = None
    digital: Optional[bool] = None
    free: Optional[bool] = None
    rating: Optional[int] = None


# File Upload Schemas
class ProductFileUploadSchema(Schema):
    preview: Optional[UploadedFile] = None
    product: Optional[UploadedFile] = None


# Response Schemas
class CategoryListResponseSchema(Schema):
    categories: list[CategorySchema] = []


class SubCategoryListResponseSchema(Schema):
    subcategories: list[SubCategorySchema] = []


class ProductListResponseSchema(Schema):
    products: list[ProductSchema] = []


class PaginatedProductResponseSchema(Schema):
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: list[ProductSchema] = []


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Specialized Response Schemas
class ProductStatsSchema(Schema):
    total_products: int
    total_buyers: int
    categories_count: int
    most_popular_product: Optional[dict] = None


class UserProductsResponseSchema(Schema):
    user_id: int
    products: list[ProductSchema] = []
    total_purchased: int


class TrendingProductsResponseSchema(Schema):
    trending_products: list[ProductSchema] = []
    period: str = "all_time"