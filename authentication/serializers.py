from .models import CustomUser
from rest_framework import serializers
from utils import get_full_image_url

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        exclude = ('password', 'groups', 'user_permissions')

    def get_avatar_url(self, obj):
        useravatar = obj.avatar
        return get_full_image_url(useravatar)
    
    # 