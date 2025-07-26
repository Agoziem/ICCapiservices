from typing import Optional
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ninja.files import UploadedFile
from ninja_jwt.authentication import JWTAuth
from ..models import Organization
from ..schemas import (
    OrganizationSchema,
    OrganizationListResponseSchema,
    CreateOrganizationSchema,
    UpdateOrganizationSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


class OrganizationPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/organizations", tags=["Organizations"])
class OrganizationsController:

    @route.get("/", response=list[OrganizationSchema])
    @paginate(OrganizationPagination)
    def list_organizations(self):
        """Get all organizations"""
        organizations = Organization.objects.all().order_by('-created_at')
        return organizations

    @route.get("/{organization_id}", response=OrganizationSchema)
    def get_organization(self, organization_id: int):
        """Get a specific organization by ID"""
        organization = get_object_or_404(Organization, id=organization_id)
        return organization

    @route.post("/", response=OrganizationSchema, auth=JWTAuth())
    def create_organization(self, payload: CreateOrganizationSchema, logo: Optional[UploadedFile] = None):
        """Create a new organization"""
        try:
            organization_data = payload.model_dump()
            if logo:
                organization_data["logo"] = logo
            organization = Organization.objects.create(**organization_data)
            return organization
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{organization_id}", response=OrganizationSchema, auth=JWTAuth()
    )
    def update_organization(
        self, organization_id: int, payload: UpdateOrganizationSchema, logo: Optional[UploadedFile] = None
    ):
        """Update an organization"""
        organization = get_object_or_404(Organization, id=organization_id)

        organization_data = payload.model_dump(exclude_unset=True)
        for attr, value in organization_data.items():
            setattr(organization, attr, value)

        if logo:
            organization.logo = logo  # type: ignore
        organization.save()

        return organization

    @route.delete(
        "/{organization_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_organization(self, organization_id: int):
        """Delete an organization"""
        organization = get_object_or_404(Organization, id=organization_id)
        organization.delete()
        return {"message": "Organization deleted successfully"}

