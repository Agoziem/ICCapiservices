from .models import CustomUser
from rest_framework import serializers
import re

class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name','last_name','username', 'email', 'avatar', 'groups', 'user_permissions', 'is_staff', 'date_joined',"emailIsVerified")

    def get_avatar(self, obj):
        useravatar = obj.avatar
        if not useravatar:
            return None 
        
        useravatar_url = useravatar.url
        if not useravatar_url.startswith(('http://', 'https://')):
            useravatar_url = f"http://127.0.0.1:8000{useravatar_url}"  
        pattern_media = r'^/media/'
        pattern_percent_3A = r'%3A'
        modified_url = re.sub(pattern_media, '', useravatar_url)
        modified_url = re.sub(pattern_percent_3A, ':/', modified_url, count=1)
        modified_url = re.sub(pattern_percent_3A, ':', modified_url)
        return modified_url