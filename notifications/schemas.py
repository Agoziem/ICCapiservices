from typing import Optional, List
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Notification, NOTIFICATION_TYPES
from authentication.schemas import UserMiniSchema


# Base Model Schema
class NotificationSchema(ModelSchema):
    users_viewed: List[UserMiniSchema] = []
    users_viewed_count: int = 0
    is_viewed_by_user: Optional[bool] = None  # Will be set dynamically for authenticated users

    class Meta:
        model = Notification
        fields = "__all__"

    @classmethod 
    def from_orm_with_user(cls, obj, user=None):
        """Create schema instance with user-specific data"""
        # Get the basic data
        data = {
            'id': obj.id,
            'title': obj.title,
            'message': obj.message,
            'type': obj.type,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        
        # Add users_viewed data if available
        if hasattr(obj, 'users_viewed'):
            users_viewed_list = list(obj.users_viewed.all())
            data['users_viewed'] = [UserMiniSchema.model_validate(u) for u in users_viewed_list]
            data['users_viewed_count'] = len(users_viewed_list)
            
            # Set user-specific viewed status
            if user:
                data['is_viewed_by_user'] = user in users_viewed_list
        else:
            data['users_viewed'] = []
            data['users_viewed_count'] = 0
            data['is_viewed_by_user'] = None if user is None else False
            
        return cls(**data)


# Input Schemas for Creating/Updating
class CreateNotificationSchema(Schema):
    title: str
    message: str
    type: Optional[str] = 'info'  # Default to 'info' type


class UpdateNotificationSchema(Schema):
    title: Optional[str] = None
    message: Optional[str] = None
    type: Optional[str] = None


# Mark notification as viewed schema
class MarkAsViewedSchema(Schema):
    notification_id: int


# Response Schemas
class NotificationListResponseSchema(Schema):
    notifications: list[NotificationSchema]

class UnreadCountResponseSchema(Schema):
    unread_count: int

class SuccessResponseSchema(Schema):
    message: str

class ErrorResponseSchema(Schema):
    error: str


# Paginated response schemas
class PaginatedNotificationResponseSchema(Schema):
    count: int
    items: list[NotificationSchema]
