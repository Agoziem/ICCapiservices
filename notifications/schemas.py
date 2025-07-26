from typing import Optional
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Notification


# Base Model Schema
class NotificationSchema(ModelSchema):
    class Meta:
        model = Notification
        fields = "__all__"


# Input Schemas for Creating/Updating
class CreateNotificationSchema(Schema):
    title: str
    message: str
    viewed: Optional[bool] = False


class UpdateNotificationSchema(Schema):
    title: Optional[str] = None
    message: Optional[str] = None
    viewed: Optional[bool] = None


# Response Schemas
class NotificationListResponseSchema(Schema):
    notifications: list[NotificationSchema]


class SuccessResponseSchema(Schema):
    message: str


class ErrorResponseSchema(Schema):
    error: str


# Paginated response schemas
class PaginatedNotificationResponseSchema(Schema):
    count: int
    items: list[NotificationSchema]
