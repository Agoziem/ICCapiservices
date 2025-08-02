from typing import Any, Optional, cast
from django.conf import settings
from ninja_extra import NinjaExtraAPI, api_controller, http_post, http_get, http_put, http_delete, paginate
from ninja_extra.pagination import LimitOffsetPagination
from ninja import Form, File
from ninja.files import UploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from ICCapiservices.redis import add_oauth_code_to_blocklist, oauth_code_in_blocklist
from ICCapp.models import Organization
from django.shortcuts import redirect
import uuid
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.exceptions import TokenError
from ninja_jwt.authentication import JWTAuth
from authentication.models import CustomUser
from authentication.routes.utils import get_tokens_for_user
from authlib.integrations.django_client import OAuth as DjangoOAuth
from django.conf import settings

from ..schemas import (
    LogoutSchema, RegisterUserSchema, RegisterUserOAuthSchema, TokenResponseSchema, VerifyUserSchema, UpdateUserSchema,
    UserSchema, RegisterUserResponseSchema, VerifyUserResponseSchema,
    ErrorResponseSchema, SuccessResponseSchema, UserMiniSchema, PaginatedUserResponseSchema
)
from utils import normalize_img_field

User = cast(type[CustomUser], get_user_model())


class UserPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000

oauth = DjangoOAuth()
oauth.register(name='google')
oauth.register(name='github')


@api_controller('/auth', tags=['Authentication'])
class AuthenticationController:

    @http_post('/register', response={201: TokenResponseSchema, 400: ErrorResponseSchema, 500: ErrorResponseSchema})
    def register_user(self, data: RegisterUserSchema):
        """Register a new user without OAuth"""
        try:
            # Check if user already exists
            existing_user = User.objects.filter(
                email=data.email, isOauth=False).first()
            if existing_user:
                return 400, {"error": "User already exists"}

            # Create new user
            new_user = User.objects.create_user(
                username=data.firstname,
                email=data.email,
                first_name=data.firstname,
                last_name=data.lastname,
                password=data.password,
                date_joined=timezone.now()
            )

            # Set verification token and expiry time
            verification_token = uuid.uuid4().hex
            new_user.verificationToken = verification_token
            new_user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
            new_user.save()

            # Check if organization ID is passed
            if data.organization_id:
                try:
                    organization = Organization.objects.get(
                        id=data.organization_id)
                    group_name = organization.name
                    group, created = Group.objects.get_or_create(
                        name=group_name)
                    new_user.groups.add(group)
                except Organization.DoesNotExist:
                    pass

            return 201, {"token": verification_token}

        except Exception as e:
            print(f"Error during user registration: {e}")
            return 500, {"error": "An error occurred during registration"}

    @http_post('/login_email', response={200: VerifyUserResponseSchema, 404: ErrorResponseSchema, 500: ErrorResponseSchema})
    def login_email(self, data: VerifyUserSchema):
        """Verify user with email and password"""
        try:
            user = User.objects.get(email=data.email, isOauth=False)
            if not user.check_password(data.password):
                return 404, {"error": "wrong password"}
            if not user.emailIsVerified:
                return 404, {"error": "Email not verified"}
            token = get_tokens_for_user(user)
            user_data = UserSchema.model_validate(user)
            return 200, {"access_token": token["access"], "refresh_token": token["refresh"], "user": user_data}

        except User.DoesNotExist:
            return 404, {"error": "User does not exist"}
        except Exception as e:
            print(e)
            return 500, {"error": "User verification failed"}

    @http_post('/logout', response={200: dict[str, str], 404: ErrorResponseSchema, 500: ErrorResponseSchema}, auth=JWTAuth())
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

    # -----------------------------------------------------------
    # Oauth login
    # -----------------------------------------------------------
    @http_get("/login-oauth/{provider}", response={400: ErrorResponseSchema})
    async def login_oauth(request, provider: str):
        redirect_uri = f"{settings.REDIRECT_URI}/{provider}"
        if not oauth.google or not oauth.github:
            return 400, {"error": "OAuth provider not configured"}
        if provider == "google":
            return await oauth.google.authorize_redirect(request, redirect_uri)
        elif provider == "github":
            return await oauth.github.authorize_redirect(request, redirect_uri)

    @http_get('/callback/{provider}', response={500: ErrorResponseSchema})
    async def auth_via_oauth(request, provider: str):
        """Register or update a user with an OAuth provider"""
        try:
            if not oauth.google or not oauth.github:
                return 400, {"error": "OAuth provider not configured"}
            if provider == "google":
                token = await oauth.google.authorize_access_token(request)
            elif provider == "github":
                token = await oauth.github.authorize_access_token(request)
            else:
                return 400, {"error": "Unsupported provider"}

            user_info = token["userinfo"]
            validated_user = RegisterUserOAuthSchema(**user_info)
            defaults = {
                "username": validated_user.name,
                "first_name": validated_user.given_name or '',
                "last_name": validated_user.family_name or '',
                "emailIsVerified": validated_user.email_verified,
                "isOauth": True,
                "Oauthprovider": provider,
                "date_joined": timezone.now(),
            }

            user, created = User.objects.update_or_create(
                email=validated_user.email, isOauth=True, Oauthprovider=provider,
                defaults=defaults
            )
            code = str(uuid.uuid4())
            await add_oauth_code_to_blocklist(code, str(user.pk))

            return redirect(
                f"{settings.SITE_DOMAIN}/oauth_success?code={code}"
            )

        except Exception as e:
            print("OAuth Registration Error:", e)
            return 500, {"error": "User registration failed"}

    @http_get('/get_oauth_token/{code}', response={200: VerifyUserResponseSchema, 400: ErrorResponseSchema, 500: ErrorResponseSchema})
    async def get_oauth_token(request, code: str):
        try:
            user_id = await oauth_code_in_blocklist(code)
            if not user_id:
                return 400, {"error": "Invalid or expired code"}
            user = get_object_or_404(User, id=user_id)
            token = get_tokens_for_user(user)
            return 200, {"access_token": token["access"], "refresh_token": token["refresh"]}
        except Exception as e:
            print("Error fetching OAuth token:", e)
            return 500, {"error": "Internal server error"}

    # --------------------------------------------------------------
    # User management
    # --------------------------------------------------------------

    @http_get('/profile', response=UserSchema, auth=JWTAuth())
    def get_user_profile(self, request):
        """Get current user profile"""
        user = request.user
        return UserSchema.model_validate(user)
    
    @http_get('/get_user_by_id/{user_id}', response=UserSchema, auth=JWTAuth())
    def get_user_by_id(self, user_id: int):
        """Get user by ID"""
        user = get_object_or_404(User, id=user_id)
        return UserSchema.model_validate(user)

    @http_get('/get_user_by_email/{email}', response=UserSchema, auth=JWTAuth())
    def get_user_by_email(self, email: str):
        """Get user by email"""
        user = get_object_or_404(User, email=email)
        return UserSchema.model_validate(user)

    @http_get('/users', response=PaginatedUserResponseSchema, auth=JWTAuth())
    @paginate(UserPagination)
    def get_users(self):
        """Get all users"""
        users = User.objects.all().order_by('-date_joined')
        return users

    @http_put('/profile', response=UserSchema, auth=JWTAuth())
    def update_user_profile(self, request, data: UpdateUserSchema, avatar: Optional[UploadedFile] = None):
        """Update current user profile"""
        user = request.user

        # Update user fields
        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(user, attr, value)
        if avatar:
            user.avatar = avatar
        user.save()
        return UserSchema.model_validate(user)

    @http_delete('/profile', response=dict[str, str], auth=JWTAuth())
    def delete_user_profile(self, request):
        """Delete current user profile"""
        user = request.user

        # Clear groups and delete user
        user.groups.clear()
        user.delete()
        return {"message": "User profile deleted successfully"}
