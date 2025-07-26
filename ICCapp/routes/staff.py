from typing import Optional
from ninja import UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from ninja_jwt.authentication import JWTAuth

from ..models import Organization, Staff
from ..schemas import (
    StaffSchema,
    StaffListResponseSchema,
    PaginatedStaffResponseSchema,
    CreateStaffSchema,
    UpdateStaffSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/staff", tags=["Staff"])
class StaffController:

    @route.get("/{organization_id}", response=PaginatedStaffResponseSchema)
    def list_staff(
        self,
        organization_id: int,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ):
        """Get all staff for an organization with pagination"""
        try:
            staff = Staff.objects.filter(organization=organization_id).order_by("id")
            if not page_size:
                page_size = 10
            paginator = Paginator(staff, page_size)
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

    @route.get("/member/{staff_id}", response=StaffSchema)
    def get_staff(self, staff_id: int):
        """Get a specific staff member by ID"""
        staff = get_object_or_404(Staff, id=staff_id)
        return staff

    @route.post(
        "/{organization_id}", response=StaffSchema, auth=JWTAuth()
    )
    def create_staff(self, organization_id: int, payload: CreateStaffSchema, img: Optional[UploadedFile] = None):
        """Create a new staff member"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            staff_data = payload.model_dump()
            if img:
                staff_data["img"] = img
            staff = Staff.objects.create(organization=organization, **staff_data)
            return staff
        except Exception as e:
            return {"error": str(e)}

    @route.put("/{staff_id}", response=StaffSchema, auth=JWTAuth())
    def update_staff(self, staff_id: int, payload: UpdateStaffSchema, img: Optional[UploadedFile] = None):
        """Update a staff member"""
        staff = get_object_or_404(Staff, id=staff_id)

        staff_data = payload.model_dump(exclude_unset=True)
        for attr, value in staff_data.items():
            setattr(staff, attr, value)

        if img:
            staff.img = img  # type: ignore
        staff.save()

        return staff

    @route.delete(
        "/{staff_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_staff(self, staff_id: int):
        """Delete a staff member"""
        staff = get_object_or_404(Staff, id=staff_id)
        staff.delete()
        return {"message": "Staff member deleted successfully"}
