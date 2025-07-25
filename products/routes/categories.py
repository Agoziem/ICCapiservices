from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from ..models import Category, SubCategory
from ..schemas import (
    CategorySchema,
    CategoryListResponseSchema,
    SubCategorySchema,
    SubCategoryListResponseSchema,
    CreateCategorySchema,
    UpdateCategorySchema,
    CreateSubCategorySchema,
    UpdateSubCategorySchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/categories", tags=["Product Categories"])
class CategoriesController:

    @route.get("/", response=list[CategorySchema])
    def get_categories(self):
        """Get all product categories"""
        categories = Category.objects.all().order_by("category")
        return categories

    @route.post("/", response=CategorySchema, permissions=[IsAuthenticated])
    def add_category(self, payload: CreateCategorySchema):
        """Create a new product category"""
        try:
            category_data = payload.model_dump()
            category = Category.objects.create(**category_data)
            return category
        except Exception as e:
            return {"error": str(e)}

    @route.get("/{category_id}", response=CategorySchema)
    def get_category(self, category_id: int):
        """Get a specific category by ID"""
        category = get_object_or_404(Category, id=category_id)
        return category

    @route.put("/{category_id}", response=CategorySchema, permissions=[IsAuthenticated])
    def update_category(self, category_id: int, payload: UpdateCategorySchema):
        """Update a category"""
        category = get_object_or_404(Category, id=category_id)

        category_data = payload.model_dump(exclude_unset=True)
        for attr, value in category_data.items():
            setattr(category, attr, value)
        category.save()

        return category

    @route.delete(
        "/{category_id}", response=SuccessResponseSchema, permissions=[IsAuthenticated]
    )
    def delete_category(self, category_id: int):
        """Delete a category"""
        category = get_object_or_404(Category, id=category_id)
        category.delete()
        return {"message": "Category deleted successfully"}


@api_controller("/subcategories", tags=["Product Subcategories"])
class SubCategoriesController:

    @route.get("/{category_id}", response=list[SubCategorySchema])
    def get_subcategories(self, category_id: int):
        """Get all subcategories for a specific category"""
        category = get_object_or_404(Category, id=category_id)
        subcategories = (
            SubCategory.objects.filter(category=category)
            .select_related("category")
            .order_by("subcategory")
        )
        return subcategories

    @route.get("/subcategory/{subcategory_id}", response=SubCategorySchema)
    def get_subcategory(self, subcategory_id: int):
        """Get a specific subcategory by ID"""
        subcategory = get_object_or_404(
            SubCategory.objects.select_related("category"), id=subcategory_id
        )
        return subcategory

    @route.post("/", response=SubCategorySchema, permissions=[IsAuthenticated])
    def create_subcategory(self, payload: CreateSubCategorySchema):
        """Create a new subcategory"""
        try:
            subcategory_data = payload.model_dump()
            category_id = subcategory_data.pop("category")

            category = get_object_or_404(Category, id=category_id)
            subcategory = SubCategory.objects.create(
                category=category, **subcategory_data
            )
            return subcategory
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{subcategory_id}", response=SubCategorySchema, permissions=[IsAuthenticated]
    )
    def update_subcategory(self, subcategory_id: int, payload: UpdateSubCategorySchema):
        """Update a subcategory"""
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)

        subcategory_data = payload.model_dump(exclude_unset=True)

        # Handle category update
        if "category" in subcategory_data:
            category_id = subcategory_data.pop("category")
            category = get_object_or_404(Category, id=category_id)
            subcategory.category = category

        # Update remaining fields
        for attr, value in subcategory_data.items():
            setattr(subcategory, attr, value)

        subcategory.save()
        return subcategory

    @route.delete(
        "/{subcategory_id}",
        response=SuccessResponseSchema,
        permissions=[IsAuthenticated],
    )
    def delete_subcategory(self, subcategory_id: int):
        """Delete a subcategory"""
        subcategory = get_object_or_404(SubCategory, id=subcategory_id)
        subcategory.delete()
        return {"message": "Subcategory deleted successfully"}

    @route.get("/all", response=list[SubCategorySchema])
    def get_all_subcategories(self):
        """Get all subcategories across all categories"""
        subcategories = SubCategory.objects.select_related("category").order_by(
            "category__category", "subcategory"
        )
        return subcategories
