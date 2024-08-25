from rest_framework import serializers
from .models import ChatGroup, GroupMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Add other relevant fields here

class GroupMessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False)
    users_seen = UserSerializer(many=True)
    reply_to = serializers.PrimaryKeyRelatedField(queryset=GroupMessage.objects.all(), required=False)

    class Meta:
        model = GroupMessage
        fields = '__all__'

class ChatGroupSerializer(serializers.ModelSerializer):
    admins = UserSerializer(many=True)
    users_online = UserSerializer(many=True)
    members = UserSerializer(many=True)
    owner = UserSerializer(many=False)
    group_messages = GroupMessageSerializer(many=True, read_only=True, source='chat_messages')

    class Meta:
        model = ChatGroup
        fields = '__all__'
