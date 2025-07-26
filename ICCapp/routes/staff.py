from typing import List, Optional
from ninja import UploadedFile
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from ..models import Organization, Staff
from ..schemas import (
    StaffSchema,
    StaffListResponseSchema,
    CreateStaffSchema,
    UpdateStaffSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)

class StaffPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/staff", tags=["Staff"])
class StaffController:

    @route.get("/{organization_id}", response={200: List[StaffSchema], 500: ErrorResponseSchema})
    @paginate(StaffPagination)
    def list_staff(
        self,
        organization_id: int,
    ):
        """Get all staff for an organization with pagination"""
        try:
            staff = Staff.objects.filter(organization=organization_id).order_by("id")
            return 200, staff
        except Exception:
            return 500, {"error": "An error occurred while fetching staff members"}

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
