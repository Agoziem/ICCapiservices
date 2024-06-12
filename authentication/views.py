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

User = get_user_model()

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


# register user with Oauth without password
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

       
# verify user with User existance
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

# get a user by ID
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
    
    
# view to update a user
@api_view(['PUT'])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.avatar = request.data.get('image', user.avatar)
        user.address = request.data.get('address', user.address)
        user.phone = request.data.get('Phonenumber', user.phone)
        user.Sex = request.data.get('sex',user.Sex)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        user.save()
        user_serializer = UserSerializer(instance=user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# remove a user and the token
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
