from typing import List
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete
from django.shortcuts import get_object_or_404
from django.http import Http404
from ninja_jwt.authentication import JWTAuth

from ..models import Category
from ..schemas import (
    CategorySchema,
    CreateCategorySchema,
    UpdateCategorySchema,
    ErrorResponseSchema,
    SuccessResponseSchema,
    CategoryListResponseSchema,
)


@api_controller("/blog-categories", tags=["Blog Categories"])
class BlogCategoriesController:

    @http_get("/", response={200: List[CategorySchema], 500: str})
    def get_categories(self):
        """Get all blog categories"""
        try:
            categories = Category.objects.all()
            return 200, [
                CategorySchema.model_validate(category) for category in categories
            ]
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_post("/", response={201: CategorySchema, 400: ErrorResponseSchema, 500: str}, auth=JWTAuth())
    def create_category(self, data: CreateCategorySchema):
        """Create a new blog category"""
        try:
            category = Category.objects.create(**data.model_dump())
            return 201, CategorySchema.model_validate(category)
        except Exception as e:
            print(e)
            return 500, "Failed to create category"

    @http_put("/{category_id}", response={200: CategorySchema, 404: str, 500: str}, auth=JWTAuth())
    def update_category(self, category_id: int, data: UpdateCategorySchema):
        """Update an existing blog category"""
        try:
            category = get_object_or_404(Category, id=category_id)

            update_data = data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(category, field) and value is not None:
                    setattr(category, field, value)

            category.save()
            return 200, CategorySchema.model_validate(category)

        except Http404:
            return 404, "Category not found"
        except Exception as e:
            print(e)
            return 500, "Failed to update category"

    @http_delete("/{category_id}", response={204: None, 404: str, 500: str}, auth=JWTAuth())
    def delete_category(self, category_id: int):
        """Delete a blog category"""
        try:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            return 204, None
        except Http404:
            return 404, "Category not found"
        except Exception as e:
            print(e)
            return 500, "Failed to delete category"

    @http_get("/{category_id}", response={200: CategorySchema, 404: str, 500: str})
    def get_category(self, category_id: int):
        """Get a specific category by ID"""
        try:
            category = get_object_or_404(Category, id=category_id)
            return 200, CategorySchema.model_validate(category)
        except Http404:
            return 404, "Category not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"
