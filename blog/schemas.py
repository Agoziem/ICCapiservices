from typing import Optional, List
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import Blog, Tag, Category, Comment
from authentication.schemas import UserMiniSchema  # This will work at runtime
from utils import get_full_image_url, get_image_name


# Define a temporary UserMiniSchema for type checking if needed
class UserMiniSchemaTemp(Schema):
    id: int
    username: str
    img: Optional[str] = None


# Base Model Schemas
class TagSchema(ModelSchema):
    class Meta:
        model = Tag
        fields = "__all__"


class CategorySchema(ModelSchema):
    class Meta:
        model = Category
        fields = "__all__"


class CommentSchema(ModelSchema):
    user: UserMiniSchemaTemp

    class Meta:
        model = Comment
        fields = "__all__"


class BlogSchema(ModelSchema):
    img_url: Optional[str] = None
    img_name: Optional[str] = None
    author: Optional[UserMiniSchemaTemp] = None
    category: Optional[CategorySchema] = None
    tags: List[TagSchema] = []
    likes_count: int = 0

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "subtitle",
            "body",
            "slug",
            "category",
            "tags",
            "author",
            "organization",
            "img",
            "readTime",
            "views",
            "date",
            "updated_at",
            "likes",
        ]

    @staticmethod
    def resolve_img_url(obj):
        return get_full_image_url(obj.img) if obj.img else None

    @staticmethod
    def resolve_img_name(obj):
        return get_image_name(obj.img) if obj.img else None

    @staticmethod
    def resolve_likes_count(obj):
        return obj.likes.count()


# Input Schemas for Blog Operations
class CreateBlogSchema(Schema):
    title: str
    subtitle: Optional[str] = None
    body: Optional[str] = None
    category: Optional[int] = None
    tags: Optional[List[str]] = []
    author: int
    organization: Optional[int] = None
    readTime: Optional[int] = 0


class UpdateBlogSchema(Schema):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    body: Optional[str] = None
    category: Optional[int] = None
    tags: Optional[List[str]] = []
    author: Optional[int] = None
    readTime: Optional[int] = None


# Input Schemas for Category Operations
class CreateCategorySchema(Schema):
    category: str
    description: Optional[str] = "None"


class UpdateCategorySchema(Schema):
    category: Optional[str] = None
    description: Optional[str] = None


# Input Schemas for Comment Operations
class CreateCommentSchema(Schema):
    comment: str


class UpdateCommentSchema(Schema):
    comment: str


# Response Schemas
class BlogListResponseSchema(Schema):
    blogs: List[BlogSchema] = []


class CategoryListResponseSchema(Schema):
    categories: List[CategorySchema] = []


class CommentListResponseSchema(Schema):
    comments: List[CommentSchema] = []


class TagListResponseSchema(Schema):
    tags: List[TagSchema] = []


class ErrorResponseSchema(Schema):
    error: str


class SuccessResponseSchema(Schema):
    message: str


class BlogDetailResponseSchema(BlogSchema):
    pass


class CategoryDetailResponseSchema(CategorySchema):
    pass


class CommentDetailResponseSchema(CommentSchema):
    pass


# Blog Statistics Schema
class BlogStatsSchema(Schema):
    total_blogs: int
    total_views: int
    total_likes: int
    total_comments: int


# Blog with Comments Schema (for detailed view)
class BlogWithCommentsSchema(BlogSchema):
    comments: List[CommentSchema] = []
    comments_count: int = 0

    @staticmethod
    def resolve_comments_count(obj):
        return obj.comment_set.count()


# Simplified schemas for listing
class BlogSummarySchema(Schema):
    id: int
    title: str
    subtitle: Optional[str] = None
    slug: Optional[str] = None
    author: Optional[UserMiniSchemaTemp] = None
    category: Optional[CategorySchema] = None
    img_url: Optional[str] = None
    views: int = 0
    likes_count: int = 0
    date: datetime
    readTime: int = 0

    @staticmethod
    def resolve_img_url(obj):
        return get_full_image_url(obj.img) if obj.img else None

    @staticmethod
    def resolve_likes_count(obj):
        return obj.likes.count()


# Like operation schemas
class LikeResponseSchema(Schema):
    liked: bool
    likes_count: int
