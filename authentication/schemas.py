from typing import Optional
from ninja import ModelSchema, Schema
from django.contrib.auth import get_user_model
from utils import get_full_image_url, get_image_name

User = get_user_model()


# Base User Schemas
class UserSchema(ModelSchema):
    avatar_url: Optional[str] = None
    avatar_name: Optional[str] = None
    
    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']
    
    @staticmethod
    def resolve_avatar_url(obj):
        return get_full_image_url(obj.avatar) if obj.avatar else None
    
    @staticmethod
    def resolve_avatar_name(obj):
        return get_image_name(obj.avatar) if obj.avatar else None


class UserMiniSchema(ModelSchema):
    img: Optional[str] = None
    
    class Meta:
        model = User
        fields = ['id', 'username']
    
    @staticmethod
    def resolve_img(obj):
        return get_full_image_url(obj.avatar) if obj.avatar else None


# Input Schemas for Authentication
class RegisterUserSchema(Schema):
    firstname: str
    lastname: str
    email: str
    password: str
    organization_id: Optional[int] = None


class RegisterUserOAuthSchema(Schema):
    name: str
    email: str
    email_verified: bool = True
    given_name: Optional[str] = None
    family_name: Optional[str] = None


class VerifyUserSchema(Schema):
    email: str
    password: str


class UpdateUserSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    avatar: Optional[str] = None  # For file uploads, you might need to handle this differently


# Token and Verification Schemas
class VerifyTokenSchema(Schema):
    token: str


class ResetPasswordSchema(Schema):
    token: str
    password: str


class GetVerificationTokenSchema(Schema):
    email: str


class VerifyEmailSchema(Schema):
    token: str


class GetUserByEmailSchema(Schema):
    email: str


# Response Schemas
class RegisterUserResponseSchema(Schema):
    token: str
    user: UserSchema


class VerifyUserResponseSchema(Schema):
    token: str
    user: UserSchema


class ErrorResponseSchema(Schema):
    error: str


class SuccessResponseSchema(Schema):
    message: str


class TokenResponseSchema(Schema):
    token: str


# Additional schemas for different response types
class UserListResponseSchema(Schema):
    users: list[UserSchema] = []


class UserDetailResponseSchema(UserSchema):
    pass
