from rest_framework import serializers
from .models import *
from utils import *

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    authordata = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = '__all__'

    def get_authordata(self, obj):
        return {'id': obj.user.id, 'name': obj.user.username, "img": get_full_image_url(obj.user.avatar) if obj.user.avatar else ""}

class BlogSerializer(serializers.ModelSerializer):
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    authordata = serializers.SerializerMethodField()
    no_of_likes = serializers.SerializerMethodField()
    category = CategorySerializer(many=False)
    tags = TagSerializer(many=True)

    class Meta:
        model = Blog
        fields = '__all__'

    
    def get_no_of_likes(self, obj):
        return obj.likes.count()
    
    def get_authordata(self, obj):
        return {'id': obj.author.id, 'name': obj.author.username, "img": get_full_image_url(obj.author.avatar) if obj.author.avatar else ""}
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.img)
    
    def get_img_name(self, obj):
        return get_image_name(obj.img)
    


