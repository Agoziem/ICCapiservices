from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import (
    Organization,
    Staff,
    Testimonial,
    Subscription,
    Department,
    DepartmentService,
)


# Base Model Schemas
class OrganizationSchema(ModelSchema):
    logo: Optional[str] = None
    logo_name: Optional[str] = None

    class Meta:
        model = Organization
        fields = "__all__"

    @staticmethod
    def resolve_logo(obj):
        return obj.logo.url if obj.logo else None

    @staticmethod
    def resolve_logo_name(obj):
        return obj.logo.name if obj.logo else None

class OrganizationMiniSchema(ModelSchema):
    id: int
    name: str

    class Meta:
        model = Organization
        fields = ["id", "name"]



class StaffSchema(ModelSchema):
    img_url: Optional[str] = None
    img_name: Optional[str] = None

    class Meta:
        model = Staff
        fields = "__all__"

    @staticmethod
    def resolve_img_url(obj):
        return obj.img.url if obj.img else None

    @staticmethod
    def resolve_img_name(obj):
        return obj.img.name if obj.img else None

class StaffMiniSchema(ModelSchema):
    id: int
    first_name: str
    last_name: str
    role: Optional[str] = None

    class Meta:
        model = Staff
        fields = ["id", "first_name", "last_name", "role", "img"]

class TestimonialSchema(ModelSchema):
    img_url: Optional[str] = None
    img_name: Optional[str] = None

    class Meta:
        model = Testimonial
        fields = "__all__"

    @staticmethod
    def resolve_img_url(obj):
        return obj.img.url if obj.img else None

    @staticmethod
    def resolve_img_name(obj):
        return obj.img.name if obj.img else None


class SubscriptionSchema(ModelSchema):
    class Meta:
        model = Subscription
        fields = "__all__"


class DepartmentServiceSchema(ModelSchema):
    class Meta:
        model = DepartmentService
        fields = "__all__"


class DepartmentSchema(ModelSchema):
    img_url: Optional[str] = None
    img_name: Optional[str] = None
    staff_in_charge: Optional[StaffMiniSchema] = None
    organization: Optional[OrganizationMiniSchema] = None
    services: list[DepartmentServiceSchema] = []

    class Meta:
        model = Department
        fields = "__all__"

    @staticmethod
    def resolve_img_url(obj):
        return obj.img.url if obj.img else None

    @staticmethod
    def resolve_img_name(obj):
        return obj.img.name if obj.img else None


# Input Schemas for Creating/Updating
class CreateOrganizationSchema(Schema):
    name: str
    description: str
    vision: str
    mission: str
    email: str
    phone: str
    address: str
    whatsapplink: Optional[str] = None
    facebooklink: Optional[str] = None
    instagramlink: Optional[str] = None
    twitterlink: Optional[str] = None
    tiktoklink: Optional[str] = None
    linkedinlink: Optional[str] = None
    youtubechannel: Optional[str] = None
    privacy_policy: Optional[str] = None
    terms_of_use: Optional[str] = None


class UpdateOrganizationSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    vision: Optional[str] = None
    mission: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    whatsapplink: Optional[str] = None
    facebooklink: Optional[str] = None
    instagramlink: Optional[str] = None
    twitterlink: Optional[str] = None
    tiktoklink: Optional[str] = None
    linkedinlink: Optional[str] = None
    youtubechannel: Optional[str] = None
    privacy_policy: Optional[str] = None
    terms_of_use: Optional[str] = None


class CreateStaffSchema(Schema):
    first_name: str
    last_name: str
    other_names: Optional[str] = None
    role: Optional[str] = "none"
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    facebooklink: Optional[str] = None
    instagramlink: Optional[str] = None
    twitterlink: Optional[str] = None
    linkedinlink: Optional[str] = None


class UpdateStaffSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    other_names: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    facebooklink: Optional[str] = None
    instagramlink: Optional[str] = None
    twitterlink: Optional[str] = None
    linkedinlink: Optional[str] = None


class CreateTestimonialSchema(Schema):
    name: str = "Anonymous"
    content: str
    role: Optional[str] = None
    rating: Optional[int] = None


class UpdateTestimonialSchema(Schema):
    name: Optional[str] = None
    content: Optional[str] = None
    role: Optional[str] = None
    rating: Optional[int] = None


class CreateSubscriptionSchema(Schema):
    email: str


class CreateDepartmentServiceSchema(Schema):
    name: str


class UpdateDepartmentServiceSchema(Schema):
    name: Optional[str] = None


class CreateDepartmentSchema(Schema):
    name: str
    description: str
    staff_in_charge: Optional[int] = None
    services: list[str]


class UpdateDepartmentSchema(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    staff_in_charge: Optional[int] = None
    services: list[str]


# Response Schemas
class OrganizationListResponseSchema(Schema):
    organizations: list[OrganizationSchema]


class StaffListResponseSchema(Schema):
    staffs: list[StaffSchema]


class TestimonialListResponseSchema(Schema):
    testimonials: list[TestimonialSchema]


class SubscriptionListResponseSchema(Schema):
    subscriptions: list[SubscriptionSchema]


class DepartmentListResponseSchema(Schema):
    departments: list[DepartmentSchema]


class DepartmentServiceListResponseSchema(Schema):
    services: list[DepartmentServiceSchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Paginated response schemas
class PaginatedOrganizationResponseSchema(Schema):
    count: int
    items: list[OrganizationSchema]


class PaginatedStaffResponseSchema(Schema):
    count: int
    items: list[StaffSchema]


class PaginatedTestimonialResponseSchema(Schema):
    count: int
    items: list[TestimonialSchema]


class PaginatedSubscriptionResponseSchema(Schema):
    count: int
    items: list[SubscriptionSchema]


class PaginatedDepartmentResponseSchema(Schema):
    count: int
    items: list[DepartmentSchema]


class PaginatedDepartmentServiceResponseSchema(Schema):
    count: int
    items: list[DepartmentServiceSchema]


