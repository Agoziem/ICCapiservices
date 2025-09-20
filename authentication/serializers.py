from .models import CustomUser
from rest_framework import serializers
from utils import *

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(allow_null=True, required=False)
    avatar_url = serializers.SerializerMethodField()
    avatar_name = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        exclude = ('password', 'groups', 'user_permissions')
        ref_name = "AuthUser"

    def get_avatar_url(self, obj):
        useravatar = obj.avatar
        return get_full_image_url(useravatar)
    
    def get_avatar_name(self, obj):
        useravatar = obj.avatar
        return get_image_name(useravatar)

class UserAuthSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    emailIsVerified = serializers.BooleanField()
    verificationToken = serializers.CharField(allow_null=True, required=False)
    expiryTime = serializers.DateTimeField(allow_null=True, required=False)
    


class UserminiSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()  # Handle avatar as URL

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'img']
        ref_name = "AuthUserMini"

    def get_img(self, obj):
        """Generate the full avatar URL or return an empty string if not available."""
        return get_full_image_url(obj.avatar) if obj.avatar else None


# Serializers for API documentation
class RegisterUserSerializer(serializers.Serializer):
    firstname = serializers.CharField(max_length=150)
    lastname = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    organization_id = serializers.IntegerField(required=False)


class RegisterUserResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = UserAuthSerializer()


class RegisterUserOauthSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    email_verified = serializers.BooleanField(default=True)
    given_name = serializers.CharField(max_length=150, required=False)
    family_name = serializers.CharField(max_length=150, required=False)


class VerifyUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class VerifyUserResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    user = UserAuthSerializer()


class UpdateUserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    address = serializers.CharField(max_length=255, required=False)
    avatar = serializers.ImageField(required=False)
    Sex = serializers.CharField(max_length=255, required=False)

class UpdateUserFCMTokenSerializer(serializers.Serializer):
    fcmToken = serializers.CharField(required=False)


class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)


class GetVerificationTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class GetUserByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class SuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField()