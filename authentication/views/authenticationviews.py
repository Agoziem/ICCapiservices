from typing import Any
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
        
        token = Token.objects.create(user=new_user)
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
        
        user_serializer = UserSerializer(instance=new_user)
        return Response({'token': token.key, 'user': user_serializer.data}, status=status.HTTP_201_CREATED)
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
        200: UserSerializer,
        201: UserSerializer,
        500: ErrorResponseSerializer
    }
)
@api_view(['POST'])
def register_user_with_oauth(request,provider):
    username = request.data['name']
    email = request.data['email']
    emailverified = request.data.get('email_verified', True)
    first_name = request.data.get('given_name', '')
    last_name = request.data.get('family_name', '')
    try:
        user = User.objects.get(email=email,isOauth=True, Oauthprovider=provider)
        user.username = username
        user.email = email
        user.emailIsVerified = emailverified
        user.first_name = first_name
        user.last_name = last_name
        user.date_joined=timezone.now()
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            username=username, 
            email=email, 
            first_name = first_name, 
            last_name = last_name, 
            emailIsVerified = emailverified, 
            isOauth=True, 
            Oauthprovider=provider,
            date_joined=timezone.now()
            )
        new_user.save()
        token = Token.objects.create(user=new_user)
        user_serializer = UserSerializer(instance=new_user)
        return Response(user_serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response({'error': 'User does not exist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
def verify_user(request):
    try:
        user = User.objects.get(email=request.data['email'],isOauth=False)
        if not user.check_password(request.data['password']):
            return Response({'error': 'wrong password'}, status=status.HTTP_404_NOT_FOUND)
        token,created = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(instance=user)
        return Response({"token": token.key, "user": user_serializer.data}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response({'error': 'User does not exist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
def get_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
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
def update_user(request, user_id):
    data = request.data.copy()
    try:
        user = User.objects.get(id=user_id)
        data = normalize_img_field(data,"avatar")
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        user.address = data.get('address', user.address)
        if data.get("avatar"):
            img = data.get("avatar")
            user.avatar = img
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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
        token = Token.objects.get(user=user)
        token.delete() 
        user.groups.clear()
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
