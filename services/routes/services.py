from typing import Optional
from ninja_extra import api_controller, route, paginate
from ninja_extra.permissions import IsAuthenticated
from ninja_extra.pagination import LimitOffsetPagination
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from django.db.models import Count
from collections import Counter
from ninja_jwt.authentication import JWTAuth

from ..models import Service, Category, SubCategory, Organization
from ..schemas import (
    ServiceSchema,
    CreateServiceSchema,
    UpdateServiceSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
    ServiceUserDetailsSchema,
)
from utils import normalize_img_field, parse_json_fields


class ServicePagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/services", tags=["Services"])
class ServicesController:

    @route.get("/{organization_id}", response=list[ServiceSchema])
    @paginate(ServicePagination)
    def get_services(self, organization_id: int, category: Optional[str] = None):
        """Get all services for a specific organization, with optional category filtering"""
        queryset = (
            Service.objects.filter(organization=organization_id)
            .select_related("organization", "category", "subcategory")
            .order_by("-updated_at")
        )

        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=service_category)
            except Category.DoesNotExist:
                pass

        # Convert to schema using the custom method
        services = []
        for service in queryset:
            services.append(ServiceSchema.from_django_model(service))

        return services

    @route.get("/trending/{organization_id}", response=list[ServiceSchema])
    @paginate(ServicePagination)
    def get_trending_services(
        self, organization_id: int, category: Optional[str] = None
    ):
        """Get trending services for a specific organization, sorted by number of buyers"""
        queryset = (
            Service.objects.filter(organization=organization_id)
            .select_related("organization", "category", "subcategory")
            .annotate(buyers_count=Count("userIDs_that_bought_this_service"))
            .filter(buyers_count__gt=0)
            .order_by("-buyers_count", "-updated_at")
        )

        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=service_category)
            except Category.DoesNotExist:
                pass

        # Convert to schema using the custom method
        services = []
        for service in queryset:
            services.append(ServiceSchema.from_django_model(service))

        return services

    @route.get("/user/{organization_id}", response=list[ServiceSchema], auth=JWTAuth())
    @paginate(ServicePagination)
    def get_user_services(
        self, request, organization_id: int, category: Optional[str] = None
    ):
        """Get services purchased by the authenticated user in an organization"""
        queryset = (
            Service.objects.filter(
                organization=organization_id,
                userIDs_that_bought_this_service__id=request.user.id,
            )
            .select_related("organization", "category", "subcategory")
            .order_by("-updated_at")
        )

        if category and category != "All":
            try:
                service_category = Category.objects.get(category=category)
                queryset = queryset.filter(category=service_category)
            except Category.DoesNotExist:
                pass

        # Convert to schema using the custom method
        services = []
        for service in queryset:
            services.append(ServiceSchema.from_django_model(service))

        return services

    @route.get("/service/{service_id}", response=ServiceSchema)
    def get_service(self, service_id: int):
        """Get details of a specific service by ID"""
        service = get_object_or_404(
            Service.objects.select_related("organization", "category", "subcategory"),
            id=service_id,
        )
        return ServiceSchema.from_django_model(service)

    @route.get("/token/{service_token}", response=ServiceSchema)
    def get_service_by_token(self, service_token: str):
        """Get details of a specific service by token"""
        service = get_object_or_404(
            Service.objects.select_related("organization", "category", "subcategory"),
            service_token=service_token,
        )
        return ServiceSchema.from_django_model(service)

    @route.post(
        "/{organization_id}", response=ServiceSchema, auth=JWTAuth()
    )
    def create_service(
        self,
        organization_id: int,
        payload: CreateServiceSchema,
        preview: Optional[UploadedFile] = None,
    ):
        """Create a new service for an organization"""
        try:
            # Get organization
            organization = get_object_or_404(Organization, id=organization_id)

            # Create service data
            service_data = payload.model_dump()
            service_data["organization"] = organization

            # Handle category
            if service_data.get("category"):
                category = get_object_or_404(Category, id=service_data.pop("category"))
                service_data["category"] = category

            # Handle subcategory
            if service_data.get("subcategory"):
                subcategory = get_object_or_404(
                    SubCategory, id=service_data.pop("subcategory")
                )
                service_data["subcategory"] = subcategory

            # Remove organization ID from service_data since we're using the object
            service_data.pop("organization", None)

            # Create service
            service = Service.objects.create(organization=organization, **service_data)

            # Handle file upload if provided
            if preview:
                service.preview = preview  # type: ignore
                service.save()

            return ServiceSchema.from_django_model(service)

        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/service/{service_id}", response=ServiceSchema, auth=JWTAuth()
    )
    def update_service(
        self,
        service_id: int,
        payload: UpdateServiceSchema,
        preview: Optional[UploadedFile] = None,
    ):
        """Update an existing service"""
        service = get_object_or_404(Service, id=service_id)

        try:
            # Update service fields
            service_data = payload.model_dump(exclude_unset=True)

            # Handle organization
            if "organization" in service_data:
                organization = get_object_or_404(
                    Organization, id=service_data.pop("organization")
                )
                service.organization = organization

            # Handle category
            if "category" in service_data:
                if service_data["category"]:
                    category = get_object_or_404(
                        Category, id=service_data.pop("category")
                    )
                    service.category = category
                else:
                    service.category = None
                    service_data.pop("category")

            # Handle subcategory
            if "subcategory" in service_data:
                if service_data["subcategory"]:
                    subcategory = get_object_or_404(
                        SubCategory, id=service_data.pop("subcategory")
                    )
                    service.subcategory = subcategory
                else:
                    service.subcategory = None
                    service_data.pop("subcategory")

            # Update remaining fields
            for attr, value in service_data.items():
                setattr(service, attr, value)

            # Handle file upload if provided
            if preview:
                service.preview = preview  # type: ignore

            service.save()
            return ServiceSchema.from_django_model(service)

        except Exception as e:
            return {"error": str(e)}

    @route.delete(
        "/service/{service_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_service(self, service_id: int):
        """Delete a service"""
        service = get_object_or_404(Service, id=service_id)
        service.delete()
        return {"message": "Service deleted successfully"}


@api_controller("/service-users", tags=["Service User Management"])
class ServiceUserController:

    @route.get("/buyers/{service_id}", response=list[ServiceUserDetailsSchema])
    @paginate(ServicePagination)
    def get_users_that_bought_service(self, service_id: int):
        """Get all users that have purchased a specific service"""
        service = get_object_or_404(Service, id=service_id)
        users = service.userIDs_that_bought_this_service.all()

        # Prepare user data with count
        user_data = []
        for user, count in Counter(users).items():
            from utils import get_full_image_url

            user_data.append(
                ServiceUserDetailsSchema(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    avatar_url=get_full_image_url(user.avatar),
                    user_count=count,
                    date_joined=user.date_joined,
                )
            )

        return user_data

    @route.get("/in-progress/{service_id}", response=list[ServiceUserDetailsSchema])
    @paginate(ServicePagination)
    def get_users_with_service_in_progress(self, service_id: int):
        """Get all users whose service is currently in progress"""
        service = get_object_or_404(Service, id=service_id)
        users = service.userIDs_whose_services_is_in_progress.all()

        # Prepare user data with count
        user_data = []
        for user, count in Counter(users).items():
            from utils import get_full_image_url

            user_data.append(
                ServiceUserDetailsSchema(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    avatar_url=get_full_image_url(user.avatar),
                    user_count=count,
                    date_joined=user.date_joined,
                )
            )

        return user_data

    @route.get("/completed/{service_id}", response=list[ServiceUserDetailsSchema])
    @paginate(ServicePagination)
    def get_users_with_completed_service(self, service_id: int):
        """Get all users whose service has been completed"""
        service = get_object_or_404(Service, id=service_id)
        users = service.userIDs_whose_services_have_been_completed.all()

        # Prepare user data with count
        user_data = []
        for user, count in Counter(users).items():
            from utils import get_full_image_url

            user_data.append(
                ServiceUserDetailsSchema(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    avatar_url=get_full_image_url(user.avatar),
                    user_count=count,
                    date_joined=user.date_joined,
                )
            )

        return user_data
