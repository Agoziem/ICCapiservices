from typing import cast
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
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
from ..jwt_utils import create_jwt_response_data

User = cast(type[CustomUser], get_user_model())

# -----------------------------------------------
#verify email with token
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Verify user email with verification token and return JWT tokens",
    request_body=VerifyEmailSerializer,
    responses={
        200: VerifyUserResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([])
def verify_email(request):
    """
    Verify user email with token and return JWT tokens
    """
    try:
        # Validate input data
        serializer = VerifyEmailSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        token = serializer.validated_data['token']
        
        # Find user with verification token
        try:
            user = User.objects.get(verificationToken=token)
        except User.DoesNotExist:
            return Response({'error': 'Invalid verification token'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check token expiry
        if not user.expiryTime:
            return Response({'error': 'Token has expired, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.expiryTime < timezone.now():
            return Response({'error': 'Token has expired, please request a new one'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify email and clear token
        user.emailIsVerified = True
        user.verificationToken = None
        user.expiryTime = None
        user.is_active = True  # Activate user account
        user.save()
        
        # Generate JWT tokens and create response
        response_data = create_jwt_response_data(user, "Email verification successful")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
# -----------------------------------------------
# get user by email
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Get user by email for email verification",
    request_body=GetUserByEmailSerializer,
    responses={
        200: SuccessResponseSerializer,
        404: ErrorResponseSerializer,
        500: "Internal server error"
    }
)
@api_view(['POST'])
@permission_classes([])
def get_user_by_email(request):
    try:
        email = request.data.get('email')
        user = User.objects.get(email=email,isOauth=False)
        if not user.emailIsVerified:
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
    
