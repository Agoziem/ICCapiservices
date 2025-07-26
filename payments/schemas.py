from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from decimal import Decimal
from .models import Orders
from ICCapp.schemas import OrganizationMiniSchema
from services.schemas import  ServiceMiniSchema
from products.schemas import ProductMiniSchema
from vidoes.schemas import VideoMiniSchema
from authentication.schemas import UserMiniSchema



# Base Model Schema
class OrderSchema(ModelSchema):
    organization: Optional[OrganizationMiniSchema] = None
    customer: Optional[UserMiniSchema] = None
    services: list[ServiceMiniSchema]
    products: list[ProductMiniSchema]
    videos: list[VideoMiniSchema]

    class Meta:
        model = Orders
        fields = "__all__"



# Input Schemas for Creating/Updating
class CreateOrderSchema(Schema):
    customerid: int
    total: Decimal
    services: list[int]
    products: list[int]
    videos: list[int]


class UpdateOrderSchema(Schema):
    organizationid: Optional[int] = None
    customerid: Optional[int] = None
    amount: Optional[Decimal] = None
    services: Optional[list[int]] = None
    products: Optional[list[int]] = None
    videos: Optional[list[int]] = None
    status: Optional[str] = None
    service_delivered: Optional[bool] = None


class VerifyPaymentSchema(Schema):
    reference: str
    customer_id: int


# Response Schemas
class OrderListResponseSchema(Schema):
    orders: list[OrderSchema]


class PaymentStatsSchema(Schema):
    totalorders: int
    totalcustomers: int
    customers: list[dict]


class CustomerStatsSchema(Schema):
    customer__id: int
    customer__username: str
    customer__count: int
    amount__sum: Optional[Decimal] = None
    amount__avg: Optional[Decimal] = None


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


class PaymentVerificationResponseSchema(Schema):
    status: str
    message: str
    order: Optional[OrderSchema] = None


# Paginated response schemas
class PaginatedOrderResponseSchema(Schema):
    count: int
    items: list[OrderSchema]
