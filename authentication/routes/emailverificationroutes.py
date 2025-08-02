from typing import cast
from ninja_extra import api_controller, http_post
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404
import uuid

from authentication.models import CustomUser
from authentication.routes.utils import get_tokens_for_user


from ..schemas import (
    TokenResponseSchema,
    VerifyEmailSchema,
    GetUserByEmailSchema,
    UserSchema,
    ErrorResponseSchema,
    SuccessResponseSchema,
    VerifyUserResponseSchema,
)

User = cast(type[CustomUser], get_user_model())


@api_controller("/auth/email-verification", tags=["Email Verification"])
class EmailVerificationController:

    @http_post(
        "/verify",
        response={
            200: VerifyUserResponseSchema,
            400: ErrorResponseSchema,
            404: ErrorResponseSchema,
            500: str,
        },
    )
    def verify_email(self, data: VerifyEmailSchema):
        """Verify user email with verification token"""
        try:
            user = User.objects.get(verificationToken=data.token)

            if not user.expiryTime or user.expiryTime < timezone.now():
                return 400, {"error": "Token has expired, please try again"}

            user.emailIsVerified = True
            user.verificationToken = None
            user.expiryTime = None
            user.save()

            # Generate tokens for the user
            token = get_tokens_for_user(user)
            return 200, {"access_token": token["access"], "refresh_token": token["refresh"], "user": UserSchema.model_validate(user)}

        except User.DoesNotExist:
            return 404, {"error": "user with the Verification Token not found"}
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_post(
        "/request",
        response={200: TokenResponseSchema, 404: ErrorResponseSchema, 500: str},
    )
    def request_email_verification_token(self, data: GetUserByEmailSchema):
        """Request a new email verification token if the user exists and email is not verified."""
        try:
            user = User.objects.get(email=data.email)

            # Only generate token if email is not verified
            if not user.emailIsVerified:
                # Clear existing token if any
                if user.verificationToken is not None:
                    user.verificationToken = None
                    user.expiryTime = None

                # Generate new token
                token = uuid.uuid4().hex
                user.verificationToken = token
                user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
                user.save()

                return 200, {"token": token}
            else:
                return 200, {"message": "Email is already verified"}

        except User.DoesNotExist:
            return 404, {"error": "User not found"}
        except Exception as e:
            print(e)
            return 500, "Internal server error"
