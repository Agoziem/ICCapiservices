from rest_framework import serializers
from .models import *
from authentication.serializers import UserSerializer

class ChatGroupSerializer(serializers.ModelSerializer):
    admins = UserSerializer(many=True)
    users_online = UserSerializer(many=True)
    members = UserSerializer(many=True)
    owner = UserSerializer(many=False)
    
    class Meta:
        model = ChatGroup
        fields = '__all__'


class GroupMessageSerializer(serializers.ModelSerializer):
    group = ChatGroupSerializer(many=False)
    author = UserSerializer(many=False)
    users_seen = UserSerializer(many=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=GroupMessage.objects.all(), required=False)
    
    class Meta:
        model = GroupMessage
        fields = '__all__'