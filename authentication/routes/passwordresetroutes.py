from ninja_extra import api_controller, http_post
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404
import uuid

from ..schemas import (
    VerifyTokenSchema, ResetPasswordSchema, GetVerificationTokenSchema,
    UserSchema, ErrorResponseSchema, SuccessResponseSchema
)

User = get_user_model()


@api_controller('/auth/password-reset', tags=['Password Reset'])
class PasswordResetController:
    
    @http_post('/verify-token', response={200: UserSchema, 400: ErrorResponseSchema, 404: ErrorResponseSchema})
    def verify_token(self, request, data: VerifyTokenSchema):
        """Verify user token for password reset"""
        try:
            user = User.objects.get(verificationToken=data.token)
            if user.expiryTime < timezone.now():
                return 400, {"error": "Token has expired, please try again"}
            
            return 200, UserSchema.model_validate(user)
            
        except User.DoesNotExist:
            return 404, {"error": "user with the Reset Password Token not found"}
        except Exception as e:
            print(e)
            return 500, {"error": "Internal server error"}

    @http_post('/reset', response={200: SuccessResponseSchema, 400: ErrorResponseSchema, 404: ErrorResponseSchema, 500: str})
    def reset_password(self, request, data: ResetPasswordSchema):
        """Reset user password using verification token"""
        try:
            user = User.objects.get(verificationToken=data.token)
            if user.expiryTime < timezone.now():
                return 400, {"error": "Token has expired, please try again"}
            
            user.set_password(data.password)
            user.verificationToken = None
            user.expiryTime = None
            user.save()
            
            return 200, {"message": "Password reset successfully"}
            
        except User.DoesNotExist:
            return 404, {"error": "user with the Reset Password Token not found"}
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_post('/get-token', response={200: SuccessResponseSchema, 404: ErrorResponseSchema, 500: str})
    def get_verification_token_by_email(self, request, data: GetVerificationTokenSchema):
        """Get verification token by email for password reset"""
        try:
            user = User.objects.get(email=data.email)
            
            # Clear existing token if any
            if user.verificationToken is not None:
                user.verificationToken = None
                user.expiryTime = None
            
            # Generate new token
            token = uuid.uuid4().hex
            user.verificationToken = token
            user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
            user.save()
            
            return 200, {"message": "Verification token sent successfully"}
            
        except User.DoesNotExist:
            return 404, {"error": "User not found"}
        except Exception as e:
            print(e)
            return 500, "Internal server error"
