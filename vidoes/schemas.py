from typing import Optional, List
from pydantic import BaseModel, Field
from ninja import Schema, File
from ninja.files import UploadedFile
from decimal import Decimal
from datetime import datetime


# Category Schemas
class CategorySchema(BaseModel):
    id: int
    category: str
    description: str

    class Config:
        from_attributes = True


class CreateCategorySchema(BaseModel):
    category: str
    description: str


class UpdateCategorySchema(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None


# SubCategory Schemas
class SubCategorySchema(BaseModel):
    id: int
    subcategory: str
    category: CategorySchema

    class Config:
        from_attributes = True


class CreateSubCategorySchema(BaseModel):
    subcategory: str
    category: int  # Category ID


class UpdateSubCategorySchema(BaseModel):
    subcategory: Optional[str] = None
    category: Optional[int] = None  # Category ID


# Organization Schema (simplified for video relationships)
class OrganizationSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# User Schema (simplified for video relationships)
class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    date_joined: datetime

    class Config:
        from_attributes = True


# Video Schemas
class VideoSchema(BaseModel):
    id: int
    title: str
    description: str
    price: Decimal
    video_token: Optional[str] = None
    number_of_times_bought: Optional[int] = 0
    created_at: datetime
    updated_at: datetime
    free: bool = False

    # Computed fields
    video_url: Optional[str] = None
    video_name: Optional[str] = None
    img_url: Optional[str] = None
    img_name: Optional[str] = None

    # Relationships
    organization: Optional[OrganizationSchema] = None
    category: Optional[CategorySchema] = None
    subcategory: Optional[SubCategorySchema] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_django_model(cls, video):
        from utils import get_full_image_url, get_image_name

        return cls(
            id=video.id,
            title=video.title,
            description=video.description,
            price=video.price,
            video_token=video.video_token,
            number_of_times_bought=video.number_of_times_bought,
            created_at=video.created_at,
            updated_at=video.updated_at,
            free=video.free,
            video_url=get_full_image_url(video.video),
            video_name=get_image_name(video.video),
            img_url=get_full_image_url(video.thumbnail),
            img_name=get_image_name(video.thumbnail),
            organization=(
                OrganizationSchema(
                    id=video.organization.id, name=video.organization.name
                )
                if video.organization
                else None
            ),
            category=(
                CategorySchema.model_validate(video.category)
                if video.category
                else None
            ),
            subcategory=(
                SubCategorySchema.model_validate(video.subcategory)
                if video.subcategory
                else None
            ),
        )


class CreateVideoSchema(BaseModel):
    title: str
    description: str
    price: Decimal = Field(default=Decimal("0.00"))
    free: bool = False
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: int  # Organization ID


class UpdateVideoSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    free: Optional[bool] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: Optional[int] = None  # Organization ID


# File Upload Schema
class VideoFileUploadSchema(Schema):
    thumbnail: Optional[UploadedFile] = None
    video: Optional[UploadedFile] = None


# Response Schemas


class CategoryListResponseSchema(BaseModel):
    results: List[CategorySchema]


class SubCategoryListResponseSchema(BaseModel):
    results: List[SubCategorySchema]



class SuccessResponseSchema(BaseModel):
    message: str


class ErrorResponseSchema(BaseModel):
    error: str


# Video User Details Schemas
class VideoUserDetailsSchema(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    user_count: int = 1
    date_joined: datetime

    class Config:
        from_attributes = True
