from typing import Optional
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from ninja.files import UploadedFile
from ninja_jwt.authentication import JWTAuth

from ICCapp.models import Organization
from ..models import Product, Category, SubCategory
from ..schemas import (
    ProductSchema,
    ProductListResponseSchema,
    PaginatedProductResponseSchema,
    CreateProductSchema,
    UpdateProductSchema,
    ProductFileUploadSchema,
    TrendingProductsResponseSchema,
    UserProductsResponseSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


class ProductPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/products", tags=["Products"])
class ProductsController:

    @route.get("/{organization_id}", response=PaginatedProductResponseSchema)
    def get_products(
        self,
        organization_id: int,
        category: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ):
        """Get all products for an organization with optional category filtering and pagination"""
        try:
            if category and category != "All":
                product_category = get_object_or_404(Category, category=category)
                products = Product.objects.filter(
                    organization=organization_id, category=product_category
                ).order_by("-last_updated_date")
            else:
                products = Product.objects.filter(
                    organization=organization_id
                ).order_by("-last_updated_date")

            # Select related and prefetch related for optimization
            products = products.select_related(
                "organization", "category", "subcategory__category"
            )
            if not page_size:
                page_size = 10
            paginator = Paginator(products, page_size)
            page_obj = paginator.get_page(page)

            return {
                "count": paginator.count,
                "next": (
                    f"?page={page_obj.next_page_number()}"
                    if page_obj.has_next()
                    else None
                ),
                "previous": (
                    f"?page={page_obj.previous_page_number()}"
                    if page_obj.has_previous()
                    else None
                ),
                "results": list(page_obj.object_list),
            }
        except Exception:
            return {"count": 0, "next": None, "previous": None, "results": []}

    @route.get("/trending/{organization_id}", response=PaginatedProductResponseSchema)
    def get_trending_products(
        self,
        organization_id: int,
        category: Optional[str] = None,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ):
        """Get trending products based on purchase count"""
        try:
            base_query = Product.objects.filter(organization=organization_id)

            if category and category != "All":
                product_category = get_object_or_404(Category, category=category)
                base_query = base_query.filter(category=product_category)

            products = (
                base_query.annotate(
                    buyers_count=Count("userIDs_that_bought_this_product")
                )
                .filter(buyers_count__gt=0)
                .order_by("-buyers_count", "-last_updated_date")
            )

            # Optimize queries
            products = products.select_related(
                "organization", "category", "subcategory__category"
            )
            if not page_size:
                page_size = 10
            paginator = Paginator(products, page_size)
            page_obj = paginator.get_page(page)

            return {
                "count": paginator.count,
                "next": (
                    f"?page={page_obj.next_page_number()}"
                    if page_obj.has_next()
                    else None
                ),
                "previous": (
                    f"?page={page_obj.previous_page_number()}"
                    if page_obj.has_previous()
                    else None
                ),
                "results": list(page_obj.object_list),
            }
        except Exception:
            return {"count": 0, "next": None, "previous": None, "results": []}

    @route.get("/user/{organization_id}", response=list[ProductSchema], auth=JWTAuth())
    @paginate(ProductPagination) 
    def get_user_products(
        self,
        request,
        organization_id: int,
        category: Optional[str] = None,
    ):
        """Get products purchased by authenticated user"""
        user = request.user
        base_query = Product.objects.filter(
            organization=organization_id,
            userIDs_that_bought_this_product__id=user.id,
        )

        if category and category != "All":
            product_category = get_object_or_404(Category, category=category)
            base_query = base_query.filter(category=product_category)

        products = base_query.order_by("-last_updated_date")

        # Optimize queries
        products = products.select_related(
            "organization", "category", "subcategory__category"
        )
        return products

    @route.get("/product/{product_id}", response=ProductSchema)
    def get_product(self, product_id: int):
        """Get a specific product by ID"""
        product = get_object_or_404(
            Product.objects.select_related(
                "organization", "category", "subcategory__category"
            ),
            id=product_id,
        )
        return product

    @route.post(
        "/{organization_id}", response=ProductSchema, auth=JWTAuth()
    )
    def add_product(
        self,
        organization_id: int,
        payload: CreateProductSchema,
        preview: Optional[UploadedFile] = None,
        product_file: Optional[UploadedFile] = None,
    ):
        """Create a new product"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            product_data = payload.model_dump()

            # Get category and subcategory
            category_id = product_data.pop("category")
            subcategory_id = product_data.pop("subcategory", None)

            category = get_object_or_404(Category, id=category_id)
            subcategory = None
            if subcategory_id:
                subcategory = get_object_or_404(SubCategory, id=subcategory_id)

            # Create product
            product = Product.objects.create(
                organization=organization,
                category=category,
                subcategory=subcategory,
                preview=preview,
                product=product_file,
                **product_data,
            )

            return product
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/product/{product_id}", response=ProductSchema, auth=JWTAuth()
    )
    def update_product(
        self,
        product_id: int,
        payload: UpdateProductSchema,
        preview: Optional[UploadedFile] = None,
        product_file: Optional[UploadedFile] = None,
    ):
        """Update a product"""
        product = get_object_or_404(Product, id=product_id)

        try:
            product_data = payload.model_dump(exclude_unset=True)

            # Handle category update
            if "category" in product_data:
                category_id = product_data.pop("category")
                category = get_object_or_404(Category, id=category_id)
                product.category = category

            # Handle subcategory update
            if "subcategory" in product_data:
                subcategory_id = product_data.pop("subcategory")
                if subcategory_id:
                    subcategory = get_object_or_404(SubCategory, id=subcategory_id)
                    product.subcategory = subcategory
                else:
                    product.subcategory = None

            # Handle file uploads
            if preview:
                product.preview = preview  # type: ignore
            if product_file:
                product.product = product_file  # type: ignore

            # Update remaining fields
            for attr, value in product_data.items():
                setattr(product, attr, value)

            product.save()
            return product
        except Exception as e:
            return {"error": str(e)}

    @route.delete(
        "/product/{product_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_product(self, product_id: int):
        """Delete a product"""
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return {"message": "Product deleted successfully"}

    @route.get("/free/{organization_id}", response=list[ProductSchema])
    def get_free_products(self, organization_id: int):
        """Get all free products for an organization"""
        products = (
            Product.objects.filter(organization=organization_id, free=True)
            .select_related("organization", "category", "subcategory__category")
            .order_by("-last_updated_date")
        )
        return products

    @route.get("/digital/{organization_id}", response=list[ProductSchema])
    def get_digital_products(self, organization_id: int):
        """Get all digital products for an organization"""
        products = (
            Product.objects.filter(organization=organization_id, digital=True)
            .select_related("organization", "category", "subcategory__category")
            .order_by("-last_updated_date")
        )
        return products

    @route.get("/physical/{organization_id}", response=list[ProductSchema])
    def get_physical_products(self, organization_id: int):
        """Get all physical products for an organization"""
        products = (
            Product.objects.filter(organization=organization_id, digital=False)
            .select_related("organization", "category", "subcategory__category")
            .order_by("-last_updated_date")
        )
        return products

    @route.post("/product/{product_id}/rate", response=ProductSchema)
    def rate_product(self, product_id: int, rating: int):
        """Rate a product (1-5 scale)"""
        product = get_object_or_404(Product, id=product_id)

        if 1 <= rating <= 5:
            product.rating = rating
            product.save()
            return product
        else:
            return {"error": "Rating must be between 1 and 5"}

    @route.get("/search/{organization_id}", response=list[ProductSchema])
    def search_products(self, organization_id: int, query: str):
        """Search products by name or description"""
        products = (
            Product.objects.filter(organization=organization_id, name__icontains=query)
            .select_related("organization", "category", "subcategory__category")
            .order_by("-last_updated_date")[:20]
        )
        return products
