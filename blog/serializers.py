from rest_framework import serializers
from .models import *
from utils import *
from authentication.serializers import UserminiSerializer

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
    img = serializers.ImageField(allow_null=True, required=False)
    img_url = serializers.SerializerMethodField()
    img_name = serializers.SerializerMethodField()
    author = UserminiSerializer(many=False)  
    category = CategorySerializer(many=False)
    tags = TagSerializer(many=True)

    class Meta:
        model = Blog
        fields = '__all__'
    
    def get_img_url(self, obj):
        return get_full_image_url(obj.img) if obj.img else None
    
    def get_img_name(self, obj):
        return get_image_name(obj.img) if obj.img else None
    


