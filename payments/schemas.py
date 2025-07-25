from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from decimal import Decimal
from .models import Orders


# Base Model Schema
class OrderSchema(ModelSchema):
    organization_details: Optional[dict] = None
    customer_details: Optional[dict] = None
    services_details: list[dict] = []
    products_details: list[dict] = []
    videos_details: list[dict] = []
    
    class Meta:
        model = Orders
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
    def resolve_customer_details(obj):
        if obj.customer:
            return {
                'id': obj.customer.id,
                'username': obj.customer.username,
                'email': obj.customer.email
            }
        return None
    
    @staticmethod
    def resolve_services_details(obj):
        return [
            {
                'id': service.id,
                'name': service.name,
                'price': str(service.price)
            }
            for service in obj.services.all()
        ]
    
    @staticmethod
    def resolve_products_details(obj):
        return [
            {
                'id': product.id,
                'name': product.name,
                'price': str(product.price)
            }
            for product in obj.products.all()
        ]
    
    @staticmethod
    def resolve_videos_details(obj):
        return [
            {
                'id': video.id,
                'title': video.title,
                'price': str(video.price)
            }
            for video in obj.videos.all()
        ]


# Input Schemas for Creating/Updating
class CreateOrderSchema(Schema):
    customerid: int
    total: Decimal
    services: Optional[list[int]] = []
    products: Optional[list[int]] = []
    videos: Optional[list[int]] = []


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
    orders: list[OrderSchema] = []


class PaymentStatsSchema(Schema):
    totalorders: int
    totalcustomers: int
    customers: list[dict] = []


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