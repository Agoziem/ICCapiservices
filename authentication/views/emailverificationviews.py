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

User = get_user_model()

# -----------------------------------------------
#verify email with token
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
    
