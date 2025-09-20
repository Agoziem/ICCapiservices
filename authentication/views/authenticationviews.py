from email import message
from typing import Any, cast
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from ..serializers import *
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Group
from django.conf import settings
from rest_framework.authtoken.models import Token
from ICCapp.models import Organization
import uuid
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from utils import normalize_img_field
from ..jwt_utils import create_jwt_response_data
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.parsers import MultiPartParser, FormParser

User = cast(type[CustomUser], get_user_model())

# -----------------------------------------------
# register user without Oauth
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Register a new user without OAuth",
    request_body=RegisterUserSerializer,
    responses={
        201: RegisterUserResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([])
def register_user(request):
    serializer = RegisterUserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data: dict[str, Any] = serializer.validated_data
    try:
        user = User.objects.get(email=data['email'], isOauth=False)
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            username=data['firstname'],
            email=data['email'],
            first_name=data['firstname'],
            last_name=data['lastname'],
            password=data['password'],
            date_joined=timezone.now()
        )
        new_user.verificationToken = uuid.uuid4().hex
        new_user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
        new_user.save()
        
        if 'organization_id' in data:
            try:
                organization = Organization.objects.get(id=data['organization_id'])
                group_name = organization.name
                group, _ = Group.objects.get_or_create(name=group_name)
                new_user.groups.add(group)
            except Organization.DoesNotExist:
                pass

        user_serializer = UserAuthSerializer(instance={
            'id': new_user.pk,
            'first_name': new_user.first_name,
            'last_name': new_user.last_name,
            'email': new_user.email,
            'emailIsVerified': new_user.emailIsVerified,
            'verificationToken': new_user.verificationToken,
            'expiryTime': new_user.expiryTime
        })
        return Response({'message': 'User registered successfully', 'user': user_serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error during user registration: {e}")
        return Response({'error': 'An error occurred during registration'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------
# register user with Oauth without password
# -----------------------------------------------
@swagger_auto_schema(
    method='post',
    operation_description="Register a new user with OAuth provider",
    request_body=RegisterUserOauthSerializer,
    responses={
        200: VerifyUserResponseSerializer,
        201: VerifyUserResponseSerializer,
        400: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([])
def register_user_with_oauth(request, provider):
    """
    Register or login user with OAuth provider and return JWT tokens
    """
    try:
        # Validate input data using serializer
        serializer = RegisterUserOauthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        username = validated_data['name']
        email = validated_data['email']
        emailverified = validated_data.get('email_verified', True)
        first_name = validated_data.get('given_name', '')
        last_name = validated_data.get('family_name', '')
        
        try:
            # User exists, update their information
            user = User.objects.get(email=email, isOauth=True, Oauthprovider=provider)
            user.username = username
            user.email = email
            user.emailIsVerified = emailverified
            user.first_name = first_name
            user.last_name = last_name
            user.date_joined = timezone.now()
            user.save()
            
            # Generate JWT tokens and create response
            response_data = create_jwt_response_data(user, "OAuth login successful")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Create new OAuth user
            new_user = User.objects.create_user(
                username=username, 
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                emailIsVerified=emailverified, 
                isOauth=True, 
                Oauthprovider=provider,
                date_joined=timezone.now()
            )
            
            # Generate JWT tokens and create response
            response_data = create_jwt_response_data(new_user, "OAuth registration successful")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        print(f"Error during OAuth user registration: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------
# verify user with User Credentials
# -----------------------------------------------

@swagger_auto_schema(
    method='post',
    operation_description="Verify user with email and password",
    request_body=VerifyUserSerializer,
    responses={
        200: VerifyUserResponseSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([])
def verify_user(request):
    """
    Authenticate user with email and password, return JWT tokens
    """
    try:
        # Validate input data using serializer
        serializer = VerifyUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Invalid input data', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        email = validated_data['email']
        password = validated_data['password']
        
        # Check if user exists
        try:
            user = User.objects.get(email=email, isOauth=False)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verify password
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user is active
        if not user.is_active:
            return Response({'error': 'User account is deactivated'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email is verified
        if not user.emailIsVerified:
            if user.verificationToken is not None:
                user.verificationToken = None
                user.expiryTime = None
            token = uuid.uuid4().hex
            user.verificationToken = token
            user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
            user.save()
            user_serializer = UserAuthSerializer(instance={
                'id': user.pk,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'emailIsVerified': user.emailIsVerified,
                'verificationToken': user.verificationToken,
                'expiryTime': user.expiryTime
            })
            return Response({'message': 'Verification email sent to your inbox', 'user': user_serializer.data}, status=status.HTTP_200_OK)
        # Generate JWT tokens and create response
        response_data = create_jwt_response_data(user, "Login successful")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error during user verification: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# ----------------------------------------------
# logout user by deleting the token
# -----------------------------------------------
@swagger_auto_schema(
    method="post",
    operation_description="Logout user by blacklisting the refresh token",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
        },
        required=["refresh"],
    ),
    responses={
        205: "Reset Content",
        400: "Bad Request",
        401: "Unauthorized",
        500: "Internal Server Error",
    },
)
@api_view(["POST"])
def logout_user(request):
    try:
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the token first
        try:
            token = RefreshToken(refresh_token)
            # Check if blacklist method exists (requires rest_framework_simplejwt.token_blacklist in INSTALLED_APPS)
            if hasattr(token, 'blacklist'):
                token.blacklist()
                message = "Logout successful - token blacklisted"
            else:
                # Fallback: just validate the token without blacklisting
                # The token will still expire naturally based on its lifetime
                message = "Logout successful - token validated"
                
        except TokenError as token_error:
            return Response({"error": f"Invalid token: {str(token_error)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": message}, status=status.HTTP_205_RESET_CONTENT)

    except Exception as e:
        print(f"Error during logout: {e}")
        return Response({"error": "An error occurred during logout"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------
# get a user by ID
# -----------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get current user Profile",
    responses={
        200: UserSerializer,
        404: "User not found",
        500: "Internal server error"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_user(request):
    user_id = request.user.id
    try:
        user = User.objects.get(id=user_id) 
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(None, status=status.HTTP_200_OK) 
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# -----------------------------------------------
# get a user by ID
# -----------------------------------------------
@swagger_auto_schema(
    method='get',
    operation_description="Get user by ID",
    responses={
        200: UserSerializer,
        404: "User not found",
        500: "Internal server error"
    }
)
@api_view(['GET'])
def get_user_by_id(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="Get all users",
    responses={
        200: UserSerializer(many=True),
        404: "Users not found",
        500: "Internal server error"
    }
)
@api_view(['GET'])
def get_users(request):
    try:
        user = User.objects.all()
        user_serializer = UserSerializer(user,many=True)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------------------
# view to update a user
# -----------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update user information",
    request_body=UpdateUserSerializer,
    responses={
        200: UserSerializer,
        404: "User not found",
        500: "Internal server error"
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_user(request, user_id):
    # Validate input data using serializer
    
    try:
        user = User.objects.get(id=user_id)
        data = request.data.copy()
        # Normalize image field for proper handling
        data = normalize_img_field(data, "avatar")

        serializer = UpdateUserSerializer(instance=user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        # Update user fields with validated data
        user.first_name = validated_data.get('first_name', user.first_name)
        user.last_name = validated_data.get('last_name', user.last_name)
        user.email = validated_data.get('email', user.email)
        user.phone = validated_data.get('phone', user.phone)
        user.address = validated_data.get('address', user.address)
        user.Sex = validated_data.get('Sex', user.Sex)
        
        # Handle avatar update
        if data.get("avatar"):
            user.avatar = data.get("avatar")
        
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during user update: {e}")
        return Response({'error': 'An error occurred during user update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------------------
# update FCM token
# -----------------------------------------------
@swagger_auto_schema(
    method='put',
    operation_description="Update user FCM token",
    request_body=UpdateUserFCMTokenSerializer,
    responses={
        200: SuccessResponseSerializer,
        404: "User not found",
        500: "Internal server error"
    }
)
@api_view(['PUT'])
def update_user_fcm_token(request):
    try:
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        serializer = UpdateUserFCMTokenSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user.fcmToken = validated_data.get('fcmToken', user.fcmToken)
        user.save()
        return Response({'message': 'FCM token updated successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during FCM token update: {e}")
        return Response({'error': 'An error occurred during FCM token update'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------------------
# remove a user and the token
# -----------------------------------------------
@swagger_auto_schema(
    method='delete',
    operation_description="Delete a user and their token",
    responses={
        204: "User deleted successfully",
        404: "User not found",
        500: "Internal server error"
    }
)
@api_view(['DELETE'])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Try to delete the user's token if it exists
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            # Token doesn't exist, continue with user deletion
            pass
        
        # Clear user groups and delete user
        user.groups.clear()
        user.delete()
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error during user deletion: {e}")
        return Response({'error': 'An error occurred during user deletion'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
