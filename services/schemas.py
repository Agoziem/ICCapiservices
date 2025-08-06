from re import S
from typing import Optional, List
from ninja import Schema, ModelSchema
from decimal import Decimal
from datetime import datetime
from ICCapp.schemas import OrganizationMiniSchema
from services.models import Category, Service, SubCategory, ServiceForm, FormField, FormSubmission


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


# Form Builder Schemas
class FormFieldSchema(ModelSchema):
    class Meta:
        model = FormField
        fields = ["id", "field_type", "label", "placeholder", "help_text", 
                 "is_required", "order", "options", "min_value", "max_value", 
                 "min_length", "max_length", "created_at", "updated_at"]


class CreateFormFieldSchema(Schema):
    field_type: str
    label: str
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    is_required: bool = False
    order: int = 0
    options: Optional[List[str]] = None  # For select, radio, checkbox
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


class UpdateFormFieldSchema(Schema):
    field_type: Optional[str] = None
    label: Optional[str] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    is_required: Optional[bool] = None
    order: Optional[int] = None
    options: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None


class ServiceFormSchema(ModelSchema):
    fields: List[FormFieldSchema]
    
    class Meta:
        model = ServiceForm
        fields = ["id", "title", "description", "is_active", "created_at", "updated_at"]


class CreateServiceFormSchema(Schema):
    title: str = "Service Application Form"
    description: Optional[str] = None
    is_active: bool = True


class UpdateServiceFormSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class FormSubmissionSchema(ModelSchema):
    user_id: int
    username: str
    
    class Meta:
        model = FormSubmission
        fields = ["id", "submission_data", "submitted_at", "updated_at"]


class CreateFormSubmissionSchema(Schema):
    submission_data: dict


class UpdateFormSubmissionSchema(Schema):
    submission_data: dict


# Paginated Form Schemas
class PaginatedServiceFormResponseSchema(Schema):
    count: int
    items: List[ServiceFormSchema]


class PaginatedFormFieldResponseSchema(Schema):
    count: int
    items: List[FormFieldSchema]


class PaginatedFormSubmissionResponseSchema(Schema):
    count: int
    items: List[FormSubmissionSchema]

