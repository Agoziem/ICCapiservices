from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from rest_framework.authtoken.models import Token
from ICCapp.models import Organization
import uuid
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


# -----------------------------------------------
# get user by token with token
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Verify user token for password reset",
    request_body=VerifyTokenSerializer,
    responses={
        200: UserSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    }
)
@api_view(['POST'])
def verify_token(request):
    try:
        token = request.data.get('token')
        user = User.objects.get(verificationToken=token)
        if user.expiryTime < timezone.now():
            return Response({'error': 'Token has expired, please try again'}, status=status.HTTP_400_BAD_REQUEST)
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'user with the Reset Password Token not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# -----------------------------------------------
# change password and clear token and expiry time
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Reset user password using verification token",
    request_body=ResetPasswordSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        500: "Internal server error"
    }
)
@api_view(['POST'])
def reset_password(request):
    try:
        token = request.data.get('token')
        user = User.objects.get(verificationToken=token)
        if user.expiryTime < timezone.now():
            return Response({'error': 'Token has expired, please try again'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(request.data.get('password'))
        user.verificationToken = None
        user.expiryTime = None
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'user with the Reset Password Token not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# -----------------------------------------------
# get user with email and send token
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Get verification token by email for password reset",
    request_body=GetVerificationTokenSerializer,
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
        500: "Internal server error"
    }
)
@api_view(['POST'])
def get_verification_token_by_email(request):
    try:
        email = request.data.get('email')
        user = User.objects.get(email=email,isOauth=False)
        if user.verificationToken is not None:
            user.verificationToken = None
            user.expiryTime = None
        token = uuid.uuid4().hex
        user.verificationToken = token
        user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

