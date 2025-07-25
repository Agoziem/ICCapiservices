from typing import List, Optional
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete
from ninja import File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.http import Http404

from ..models import Blog, Tag, Category
from ICCapp.models import Organization
from ..schemas import (
    BlogSchema,
    CreateBlogSchema,
    UpdateBlogSchema,
    BlogSummarySchema,
    BlogWithCommentsSchema,
    ErrorResponseSchema,
    SuccessResponseSchema,
    BlogListResponseSchema,
    BlogStatsSchema,
)
from utils import normalize_img_field

User = get_user_model()


@api_controller("/blogs", tags=["Blogs"])
class BlogsController:

    @http_get(
        "/organization/{organization_id}",
        response={200: List[BlogSchema], 404: str, 500: str},
    )
    def get_org_blogs(self, organization_id: int):
        """Get all blogs for a specific organization"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            blogs = (
                Blog.objects.filter(organization=organization)
                .select_related("author", "category")
                .prefetch_related("tags", "likes")
            )
            return 200, [BlogSchema.model_validate(blog) for blog in blogs]
        except Http404:
            return 404, "Organization not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get("/user/{user_id}", response={200: List[BlogSchema], 404: str, 500: str})
    def get_user_blogs(self, user_id: int):
        """Get all blogs by a specific user"""
        try:
            user = get_object_or_404(User, id=user_id)
            blogs = (
                Blog.objects.filter(author=user)
                .select_related("author", "category")
                .prefetch_related("tags", "likes")
            )
            return 200, [BlogSchema.model_validate(blog) for blog in blogs]
        except Http404:
            return 404, "User not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get("/{blog_id}", response={200: BlogWithCommentsSchema, 404: str, 500: str})
    def get_blog(self, blog_id: int):
        """Get a specific blog by ID with comments"""
        try:
            blog = get_object_or_404(
                Blog.objects.select_related("author", "category").prefetch_related(
                    "tags", "likes", "comment_set__user"
                ),
                id=blog_id,
            )
            return 200, BlogWithCommentsSchema.model_validate(blog)
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get(
        "/slug/{slug}", response={200: BlogWithCommentsSchema, 404: str, 500: str}
    )
    def get_blog_by_slug(self, slug: str):
        """Get a specific blog by slug with comments"""
        try:
            blog = get_object_or_404(
                Blog.objects.select_related("author", "category").prefetch_related(
                    "tags", "likes", "comment_set__user"
                ),
                slug=slug,
            )
            return 200, BlogWithCommentsSchema.model_validate(blog)
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_post(
        "/organization/{organization_id}/user/{user_id}",
        response={201: BlogSchema, 400: ErrorResponseSchema, 404: str, 500: str},
    )
    def create_blog(
        self,
        organization_id: int,
        user_id: int,
        data: CreateBlogSchema,
        img: Optional[File[UploadedFile]] = None,
    ):
        """Create a new blog post"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            author = get_object_or_404(User, id=user_id)

            # Create blog instance
            blog_data = data.model_dump(exclude={"tags"})
            blog_data["organization"] = organization
            blog_data["author"] = author

            # Generate slug from title
            if data.title:
                blog_data["slug"] = slugify(data.title)
                # Ensure unique slug
                counter = 1
                original_slug = blog_data["slug"]
                while Blog.objects.filter(slug=blog_data["slug"]).exists():
                    blog_data["slug"] = f"{original_slug}-{counter}"
                    counter += 1

            if img:
                blog_data["img"] = img

            blog = Blog.objects.create(**blog_data)

            # Handle tags
            if data.tags:
                for tag_name in data.tags:
                    tag, created = Tag.objects.get_or_create(tag=tag_name)
                    blog.tags.add(tag)

            return 201, BlogSchema.model_validate(blog)

        except Http404 as e:
            return 404, str(e)
        except Exception as e:
            print(e)
            return 500, "Failed to create blog"

    @http_put(
        "/{blog_id}",
        response={200: BlogSchema, 400: ErrorResponseSchema, 404: str, 500: str},
    )
    def update_blog(
        self,
        blog_id: int,
        data: UpdateBlogSchema,
        img: Optional[File[UploadedFile]] = None,
    ):
        """Update an existing blog post"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)

            # Update fields
            update_data = data.model_dump(exclude_unset=True, exclude={"tags"})
            for field, value in update_data.items():
                if hasattr(blog, field) and value is not None:
                    setattr(blog, field, value)

            # Update slug if title changed
            if data.title and data.title != blog.title:
                new_slug = slugify(data.title)
                counter = 1
                original_slug = new_slug
                while Blog.objects.filter(slug=new_slug).exclude(id=blog_id).exists():
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1
                blog.slug = new_slug

            if img:
                blog.img = img  # type: ignore

            blog.save()

            # Handle tags
            if data.tags is not None:
                blog.tags.clear()
                for tag_name in data.tags:
                    tag, created = Tag.objects.get_or_create(tag=tag_name)
                    blog.tags.add(tag)

            return 200, BlogSchema.model_validate(blog)

        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Failed to update blog"

    @http_delete("/{blog_id}", response={204: None, 404: str, 500: str})
    def delete_blog(self, blog_id: int):
        """Delete a blog post"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            blog.delete()
            return 204, None
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Failed to delete blog"

    @http_post(
        "/{blog_id}/view", response={200: SuccessResponseSchema, 404: str, 500: str}
    )
    def add_view(self, blog_id: int):
        """Increment blog view count"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            blog.views += 1
            blog.save()
            return 200, {"message": "View added successfully"}
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Failed to add view"

    @http_get("/", response={200: List[BlogSummarySchema], 500: str})
    def get_all_blogs(self):
        """Get all blogs (summary view)"""
        try:
            blogs = Blog.objects.select_related("author", "category").prefetch_related(
                "likes"
            )
            return 200, [BlogSummarySchema.model_validate(blog) for blog in blogs]
        except Exception as e:
            print(e)
            return 500, "Internal server error"
