from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import *
from utils import *
from authentication.serializers import UserminiSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = UserminiSerializer(many=False)
    class Meta:
        model = Comment
        fields = '__all__'



class BlogSerializer(serializers.ModelSerializer):
    # Image fields
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    author = UserminiSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'subtitle', 'body', 'slug' , 'category' , 'tags'
            , 'author', 'organization', 
            'img', 'img_url', 'img_name', 'readTime', 
            'views', 'date', 'updated_at','likes'
        ]
        read_only_fields = ['id', 'date', 'updated_at', 'views', 'likes']
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.img) if obj.img else None
    
    def get_img_name(self, obj):
        return get_image_name(obj.img) if obj.img else None
    
   

    


