from rest_framework import serializers
from .models import *

class BlogSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()
    no_of_likes = serializers.SerializerMethodField()
    no_of_comments = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    class Meta:
        model = Blog
        fields = '__all__'

    def get_no_of_likes(self, obj):
        return obj.likes.count()
    
    def get_likes(self, obj):
        return obj.likes.values_list('username', flat=True)
    
    def get_comments(self, obj):
        return obj.comments.values_list('content', flat=True)
    
    def get_no_of_comments(self, obj):
        return obj.comments.count()

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'