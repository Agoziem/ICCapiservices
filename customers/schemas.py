from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Customer


# Base Model Schema
class CustomerSchema(ModelSchema):
    class Meta:
        model = Customer
        fields = "__all__"


# Input Schemas for Creating/Updating
class CreateCustomerSchema(Schema):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None


class UpdateCustomerSchema(Schema):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


# Response Schemas
class CustomerListResponseSchema(Schema):
    customers: list[CustomerSchema] = []


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str
