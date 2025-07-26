from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Email, EmailResponse, EmailMessage


# Base Model Schemas
class EmailSchema(ModelSchema):
    class Meta:
        model = Email
        fields = "__all__"


class EmailResponseSchema(ModelSchema):
    class Meta:
        model = EmailResponse
        fields = "__all__"


class EmailMessageSchema(ModelSchema):
    class Meta:
        model = EmailMessage
        fields = "__all__"


# Input Schemas for Creating/Updating
class CreateEmailSchema(Schema):
    name: str
    email: str
    subject: str
    message: str


class UpdateEmailSchema(Schema):
    name: Optional[str] = None
    email: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None


class CreateEmailResponseSchema(Schema):
    message: int  # Foreign key to Email
    recipient_email: str
    response_subject: str
    response_message: str


class UpdateEmailResponseSchema(Schema):
    recipient_email: Optional[str] = None
    response_subject: Optional[str] = None
    response_message: Optional[str] = None


class CreateEmailMessageSchema(Schema):
    subject: str
    body: str
    template: Optional[str] = None


class UpdateEmailMessageSchema(Schema):
    subject: Optional[str] = None
    body: Optional[str] = None
    template: Optional[str] = None
    status: Optional[str] = None


# Response Schemas
class EmailListResponseSchema(Schema):
    emails: list[EmailSchema]


class EmailResponseListSchema(Schema):
    responses: list[EmailResponseSchema]


class EmailMessageListSchema(Schema):
    messages: list[EmailMessageSchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Paginated response schemas
class PaginatedEmailResponseSchema(Schema):
    count: int
    items: list[EmailSchema]


class PaginatedEmailMessageResponseSchema(Schema):
    count: int
    items: list[EmailMessageSchema]
