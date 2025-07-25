from typing import Any, Optional, cast
from ninja_extra import (
    NinjaExtraAPI,
    api_controller,
    http_post,
    http_get,
    http_put,
    http_delete,
)
from ninja import Form, File
from ninja.files import UploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from ICCapp.models import Organization
import uuid
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError
from authentication.models import CustomUser
from authentication.routes.utils import get_tokens_for_user

from ..schemas import (
    LogoutSchema,
    RegisterUserSchema,
    RegisterUserOAuthSchema,
    VerifyUserSchema,
    UpdateUserSchema,
    UserSchema,
    RegisterUserResponseSchema,
    VerifyUserResponseSchema,
    ErrorResponseSchema,
    SuccessResponseSchema,
    UserMiniSchema,
)
from utils import normalize_img_field

User = cast(type[CustomUser], get_user_model())


@api_controller("/auth", tags=["Authentication"])
class AuthenticationController:

    @http_post(
        "/register",
        response={201: UserSchema, 400: ErrorResponseSchema, 500: ErrorResponseSchema},
    )
    def register_user(self, data: RegisterUserSchema):
        """Register a new user without OAuth"""
        try:
            # Check if user already exists
            existing_user = User.objects.filter(email=data.email, isOauth=False).first()
            if existing_user:
                return 400, {"error": "User already exists"}

            # Create new user
            new_user = User.objects.create_user(
                username=data.firstname,
                email=data.email,
                first_name=data.firstname,
                last_name=data.lastname,
                password=data.password,
                date_joined=timezone.now(),
            )

            # Set verification token and expiry time
            verification_token = uuid.uuid4().hex
            new_user.verificationToken = verification_token
            new_user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
            new_user.save()

            # Check if organization ID is passed
            if data.organization_id:
                try:
                    organization = Organization.objects.get(id=data.organization_id)
                    group_name = organization.name
                    group, created = Group.objects.get_or_create(name=group_name)
                    new_user.groups.add(group)
                except Organization.DoesNotExist:
                    pass

            user_data = UserSchema.model_validate(new_user)
            return 201, user_data

        except Exception as e:
            print(f"Error during user registration: {e}")
            return 500, {"error": "An error occurred during registration"}

    @http_post(
        "/register-oauth/{provider}",
        response={
            200: RegisterUserResponseSchema,
            201: RegisterUserResponseSchema,
            500: ErrorResponseSchema,
        },
    )
    def register_user_with_oauth(self, provider: str, data: RegisterUserOAuthSchema):
        """Register or update a user with an OAuth provider"""
        try:
            defaults = {
                "username": data.name,
                "first_name": data.given_name or "",
                "last_name": data.family_name or "",
                "emailIsVerified": data.email_verified,
                "isOauth": True,
                "Oauthprovider": provider,
                "date_joined": timezone.now(),
            }

            user, created = User.objects.update_or_create(
                email=data.email,
                isOauth=True,
                Oauthprovider=provider,
                defaults=defaults,
            )

            access_token, refresh_token = get_tokens_for_user(user)
            user_data = UserSchema.model_validate(user)

            return (201 if created else 200), {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_data,
            }

        except Exception as e:
            print("OAuth Registration Error:", e)
            return 500, {"error": "User registration failed"}

    @http_post(
        "/verify",
        response={
            200: VerifyUserResponseSchema,
            404: ErrorResponseSchema,
            500: ErrorResponseSchema,
        },
    )
    def verify_user(self, data: VerifyUserSchema):
        """Verify user with email and password"""
        try:
            user = User.objects.get(email=data.email, isOauth=False)
            if not user.check_password(data.password):
                return 404, {"error": "wrong password"}
            if not user.emailIsVerified:
                return 404, {"error": "Email not verified"}
            refresh_token, access_token = get_tokens_for_user(user)
            user_data = UserSchema.model_validate(user)
            return 200, {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": user_data,
            }

        except User.DoesNotExist:
            return 404, {"error": "User does not exist"}
        except Exception as e:
            print(e)
            return 500, {"error": "User verification failed"}

    @http_post(
        "/logout",
        response={
            200: dict[str, str],
            404: ErrorResponseSchema,
            500: ErrorResponseSchema,
        },
    )
    def logout(request, data: LogoutSchema):
        """
        Blacklist the provided refresh token to log the user out.
        """
        try:
            token = RefreshToken(data.refresh)
            token.blacklist()  # This blacklists the token in the DB
            return {"detail": "Logout successful. Token blacklisted."}, 200
        except TokenError:
            return {"error": "Invalid token"}, 400
        except Exception as e:
            return {"error": str(e)}, 500

    # --------------------------------------------
    # User management
    # --------------------------------------------
    @http_get("/users/{user_id}", response={200: UserSchema, 404: str, 500: str})
    def get_user(self, user_id: int):
        """Get user by ID"""
        try:
            user = get_object_or_404(User, id=user_id)
            return 200, UserSchema.model_validate(user)
        except Http404:
            return 404, "User not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get("/users", response={200: list[UserSchema], 404: str, 500: str})
    def get_users(self):
        """Get all users"""
        try:
            users = User.objects.all()
            return 200, [UserSchema.model_validate(user) for user in users]
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_put("/users/{user_id}", response={200: UserSchema, 404: str, 500: str})
    def update_user(
        self,
        user_id: int,
        data: UpdateUserSchema,
        avatar: Optional[UploadedFile] = None,
    ):
        """Update user information"""
        try:
            user = get_object_or_404(User, id=user_id)

            # Update user fields
            for attr, value in data.model_dump(exclude_unset=True).items():
                if attr == "avatar" and avatar:
                    value = normalize_img_field(avatar, "avatar")
                setattr(user, attr, value)
            user.save()
            return 200, UserSchema.model_validate(user)

        except Http404:
            return 404, "User not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_delete("/users/{user_id}", response={204: None, 404: str, 500: str})
    def delete_user(self, user_id: int):
        """Delete a user and their token"""
        try:
            user = get_object_or_404(User, id=user_id)

            # Clear groups and delete user
            user.groups.clear()
            user.delete()
            return 204, None

        except Http404:
            return 404, "User not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"
