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

    def get_avatar_url(self, obj):
        useravatar = obj.avatar
        return get_full_image_url(useravatar)
    
    def get_avatar_name(self, obj):
        useravatar = obj.avatar
        return get_image_name(useravatar)


class UserminiSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()  # Handle avatar as URL

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'img']

    def get_img(self, obj):
        """Generate the full avatar URL or return an empty string if not available."""
        return get_full_image_url(obj.avatar) if obj.avatar else ""