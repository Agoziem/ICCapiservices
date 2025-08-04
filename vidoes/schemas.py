from typing import Optional, List
from pydantic import Field
from ninja import Schema, ModelSchema
from ninja.files import UploadedFile
from decimal import Decimal
from datetime import datetime

from ICCapp.schemas import OrganizationMiniSchema
from services.models import SubCategory
from vidoes.models import Category, Video


# Category Schemas
class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"

class CreateCategorySchema(Schema):
    category: str
    description: str


class UpdateCategorySchema(Schema):
    category: Optional[str] = None
    description: Optional[str] = None


# SubCategory Schemas
class SubCategorySchema(ModelSchema):
    class Meta:
        model = SubCategory
        fields = "__all__"


class CreateSubCategorySchema(Schema):
    subcategory: str
    category: int  # Category ID


class UpdateSubCategorySchema(Schema):
    subcategory: Optional[str] = None
    category: Optional[int] = None  # Category ID



# Video Schemas
class VideoSchema(ModelSchema):
    organization: Optional[OrganizationMiniSchema] = None
    category: Optional[CategorySchema] = None
    subcategory: Optional[SubCategorySchema] = None

    class Meta:
        model = Video
        fields = "__all__"
    

class VideoMiniSchema(Schema):
    id: int
    title: str
    price: Decimal
    free: bool = False


class CreateVideoSchema(Schema):
    title: str
    description: str
    price: Decimal = Field(default=Decimal("0.00"))
    free: bool = False
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: int  # Organization ID


class UpdateVideoSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    free: Optional[bool] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: Optional[int] = None  # Organization ID


# Response Schemas
class CategoryListResponseSchema(Schema):
    results: List[CategorySchema]


class SubCategoryListResponseSchema(Schema):
    results: List[SubCategorySchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Video User Details Schemas
class VideoUserDetailsSchema(Schema):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    user_count: int = 1
    date_joined: datetime


# Paginated response schemas
class PaginatedVideoResponseSchema(Schema):
    count: int
    items: List[VideoSchema]


class PaginatedVideoUserResponseSchema(Schema):
    count: int
    items: List[VideoUserDetailsSchema]
