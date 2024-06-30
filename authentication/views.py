from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings
from rest_framework.authtoken.models import Token
from ICCapp.models import Organization
import uuid
from django.utils import timezone

User = get_user_model()

# -----------------------------------------------
# register user without Oauth
# -----------------------------------------------
@api_view(['POST'])
def register_user(request):
    try:
        user = User.objects.get(email=request.data['email'],isOauth=False)
        return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        new_user = User.objects.create_user(
            username=request.data['firstname'],
            email=request.data['email'],
            first_name=request.data['firstname'],
            last_name=request.data['lastname'],
            password=request.data['password']
        )
        token = Token.objects.create(user=new_user)
        token = uuid.uuid4().hex
        new_user.verificationToken = token
        new_user.expiryTime = timezone.now() + timezone.timedelta(hours=2)
        new_user.save()
        # Check if organization ID is passed in the request
        if 'organization_id' in request.data:
            try:
                organization = Organization.objects.get(id=request.data['organization_id'])
                group_name = organization.name
                group, created = Group.objects.get_or_create(name=group_name)
                new_user.groups.add(group)
            except Organization.DoesNotExist:
                pass
        user_serializer = UserSerializer(instance=new_user)
        return Response({'token': token.key, 'user': user_serializer.data}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return Response({'error': 'User does not exist'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# -----------------------------------------------
# register user with Oauth without password
# -----------------------------------------------
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
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        new_user = User.objects.create_user(username=username, email=email, first_name = first_name, last_name = last_name, emailIsVerified = emailverified, isOauth=True, Oauthprovider=provider)
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
    
# -----------------------------------------------
# get user by token
# -----------------------------------------------
@api_view(['POST'])
def verify_email(request):
    try:
        token = request.data.get('token')
        user = User.objects.get(verificationToken=token)
        if user.expiryTime < timezone.now():
            return Response({'error': 'Token has expired, please try again'}, status=status.HTTP_400_BAD_REQUEST)
        user.emailIsVerified = True
        user.verificationToken = None
        user.expiryTime = None
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': 'user with the Verification Token not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# -----------------------------------------------
# get user by email
# -----------------------------------------------
@api_view(['POST'])
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
    

# -----------------------------------------------
# view to update a user
# -----------------------------------------------
@api_view(['PUT'])
def update_user(request, user_id):
    data = request.data.copy()
    try:
        user = User.objects.get(id=user_id)
        data = normalize_img_field(data,"avatar")
        user_serializer = UserSerializer(instance=user, data=data)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# -----------------------------------------------
# remove a user and the token
# -----------------------------------------------
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
