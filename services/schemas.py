from re import S
from typing import Optional, List
from ninja import Schema, ModelSchema
from decimal import Decimal
from datetime import datetime
from ICCapp.schemas import OrganizationMiniSchema
from services.models import Category, Service, SubCategory


# Category Schemas
class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"


class CreateCategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = ['category', 'description']


class UpdateCategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = ['category', 'description']


# SubCategory Schemas
class SubCategorySchema(ModelSchema):
    class Meta:
        model = SubCategory
        fields = "__all__"


class CreateSubCategorySchema(ModelSchema):
    class Meta:
        model = SubCategory
        fields = ['subcategory', 'category']


class UpdateSubCategorySchema(ModelSchema):
    class Meta:
        model = SubCategory
        fields = ['subcategory', 'category']


# Service Schemas
class ServiceSchema(ModelSchema):
    organization: Optional[OrganizationMiniSchema] = None
    category: Optional[CategorySchema] = None
    subcategory: Optional[SubCategorySchema] = None

    class Meta:
        model = Service
        fields = "__all__"

class ServiceMiniSchema(ModelSchema):
    class Meta:
        model = Service
        fields = ['id', 'name', 'description', 'price', 'preview']


class CreateServiceSchema(Schema):
    name: str
    description: Optional[str] = None
    service_flow: Optional[str] = None
    price: Decimal
    details_form_link: Optional[str] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: int  # Organization ID


class UpdateServiceSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    service_flow: Optional[str] = None
    price: Optional[Decimal] = None
    details_form_link: Optional[str] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: Optional[int] = None  # Organization ID


class CategoryListResponseSchema(Schema):
    results: List[CategorySchema]


class SubCategoryListResponseSchema(Schema):
    results: List[SubCategorySchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Service User Details Schemas
class ServiceUserDetailsSchema(Schema):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    user_count: int = 1
    date_joined: datetime



# Paginated response schemas
class PaginatedServiceResponseSchema(Schema):
    count: int
    items: List[ServiceSchema]


class PaginatedCategoryResponseSchema(Schema):
    count: int
    items: List[CategorySchema]


class PaginatedSubCategoryResponseSchema(Schema):
    count: int
    items: List[SubCategorySchema]


class PaginatedServiceUserResponseSchema(Schema):
    count: int
    items: List[ServiceUserDetailsSchema]

