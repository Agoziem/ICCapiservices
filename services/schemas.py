from typing import Optional, List
from pydantic import BaseModel, Field
from ninja import Schema
from decimal import Decimal
from datetime import datetime


# Category Schemas
class CategorySchema(BaseModel):
    id: int
    category: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class CreateCategorySchema(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None


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


# Organization Schema (simplified for service relationships)
class OrganizationSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True





# Service Schemas
class ServiceSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    service_token: Optional[str] = None
    service_flow: Optional[str] = None
    price: Decimal
    number_of_times_bought: Optional[int] = 0
    details_form_link: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Computed fields
    img_url: Optional[str] = None
    img_name: Optional[str] = None

    # Relationships
    organization: Optional[OrganizationSchema] = None
    category: Optional[CategorySchema] = None
    subcategory: Optional[SubCategorySchema] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_django_model(cls, service):
        from utils import get_full_image_url, get_image_name

        return cls(
            id=service.id,
            name=service.name,
            description=service.description,
            service_token=service.service_token,
            service_flow=service.service_flow,
            price=service.price,
            number_of_times_bought=service.number_of_times_bought,
            details_form_link=service.details_form_link,
            created_at=service.created_at,
            updated_at=service.updated_at,
            img_url=get_full_image_url(service.preview),
            img_name=get_image_name(service.preview),
            organization=(
                OrganizationSchema(
                    id=service.organization.id, name=service.organization.name
                )
                if service.organization
                else None
            ),
            category=(
                CategorySchema.model_validate(service.category)
                if service.category
                else None
            ),
            subcategory=(
                SubCategorySchema.model_validate(service.subcategory)
                if service.subcategory
                else None
            ),
        )

class ServiceMiniSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    img_url: Optional[str] = None

    class Config:
        from_attributes = True

class CreateServiceSchema(BaseModel):
    name: str
    description: Optional[str] = None
    service_flow: Optional[str] = None
    price: Decimal
    details_form_link: Optional[str] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: int  # Organization ID


class UpdateServiceSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    service_flow: Optional[str] = None
    price: Optional[Decimal] = None
    details_form_link: Optional[str] = None
    category: Optional[int] = None  # Category ID
    subcategory: Optional[int] = None  # SubCategory ID
    organization: Optional[int] = None  # Organization ID


class CategoryListResponseSchema(BaseModel):
    results: List[CategorySchema]


class SubCategoryListResponseSchema(BaseModel):
    results: List[SubCategorySchema]


class SuccessResponseSchema(BaseModel):
    message: str


class ErrorResponseSchema(BaseModel):
    error: str


# Service User Details Schemas
class ServiceUserDetailsSchema(BaseModel):
    id: int
    username: str
    email: str
    avatar_url: Optional[str] = None
    user_count: int = 1
    date_joined: datetime

    class Config:
        from_attributes = True


# Paginated response schemas
class PaginatedServiceResponseSchema(BaseModel):
    count: int
    items: List[ServiceSchema]


class PaginatedCategoryResponseSchema(BaseModel):
    count: int
    items: List[CategorySchema]


class PaginatedSubCategoryResponseSchema(BaseModel):
    count: int
    items: List[SubCategorySchema]


class PaginatedServiceUserResponseSchema(BaseModel):
    count: int
    items: List[ServiceUserDetailsSchema]

