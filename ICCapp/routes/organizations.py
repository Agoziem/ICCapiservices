from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ninja.files import UploadedFile
from ..models import Organization
from ..schemas import (
    OrganizationSchema,
    OrganizationListResponseSchema,
    CreateOrganizationSchema,
    UpdateOrganizationSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/organizations", tags=["Organizations"])
class OrganizationsController:

    @route.get("/", response=OrganizationListResponseSchema)
    def list_organizations(self):
        """Get all organizations"""
        try:
            organizations = Organization.objects.all()
            return {"organizations": list(organizations)}
        except Exception:
            return {"organizations": []}

    @route.get("/{organization_id}", response=OrganizationSchema)
    def get_organization(self, organization_id: int):
        """Get a specific organization by ID"""
        organization = get_object_or_404(Organization, id=organization_id)
        return organization

    @route.post("/", response=OrganizationSchema, permissions=[IsAuthenticated])
    def create_organization(self, payload: CreateOrganizationSchema):
        """Create a new organization"""
        try:
            organization_data = payload.model_dump()
            organization = Organization.objects.create(**organization_data)
            return organization
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{organization_id}", response=OrganizationSchema, permissions=[IsAuthenticated]
    )
    def update_organization(
        self, organization_id: int, payload: UpdateOrganizationSchema
    ):
        """Update an organization"""
        organization = get_object_or_404(Organization, id=organization_id)

        organization_data = payload.model_dump(exclude_unset=True)
        for attr, value in organization_data.items():
            setattr(organization, attr, value)
        organization.save()

        return organization

    @route.delete(
        "/{organization_id}",
        response=SuccessResponseSchema,
        permissions=[IsAuthenticated],
    )
    def delete_organization(self, organization_id: int):
        """Delete an organization"""
        organization = get_object_or_404(Organization, id=organization_id)
        organization.delete()
        return {"message": "Organization deleted successfully"}

    @route.post(
        "/{organization_id}/upload-logo",
        response=OrganizationSchema,
        permissions=[IsAuthenticated],
    )
    def upload_organization_logo(
        self, organization_id: int, logo: Optional[UploadedFile] = None
    ):
        """Upload logo for organization"""
        organization = get_object_or_404(Organization, id=organization_id)
        organization.logo = logo  # type: ignore
        # Note: Ensure that the logo field in the Organization model is set to accept InMemoryUploadedFile
        organization.save()
        return organization
