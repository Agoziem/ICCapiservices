from typing import Optional
from ninja import UploadedFile
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from ninja_jwt.authentication import JWTAuth

from ..models import Organization, Department, DepartmentService, Staff
from ..schemas import (
    DepartmentSchema,
    DepartmentListResponseSchema,
    PaginatedDepartmentResponseSchema,
    DepartmentServiceSchema,
    DepartmentServiceListResponseSchema,
    CreateDepartmentSchema,
    UpdateDepartmentSchema,
    CreateDepartmentServiceSchema,
    UpdateDepartmentServiceSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/departments", tags=["Departments"])
class DepartmentsController:

    @route.get("/{organization_id}", response=PaginatedDepartmentResponseSchema)
    def list_departments(
        self,
        organization_id: int,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ):
        """Get all departments for an organization with pagination"""
        try:
            departments = Department.objects.filter(
                organization=organization_id
            ).order_by("name")
            if not page_size:
                page_size = 10
            paginator = Paginator(departments, page_size)
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

    @route.get("/department/{department_id}", response=DepartmentSchema)
    def get_department(self, department_id: int):
        """Get a specific department by ID"""
        department = get_object_or_404(Department, id=department_id)
        return department

    @route.post(
        "/{organization_id}", response=DepartmentSchema, auth=JWTAuth()
    )
    def create_department(self, organization_id: int, payload: CreateDepartmentSchema, img: Optional[UploadedFile] = None):
        """Create a new department"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            department_data = payload.model_dump()
            # Extract services and staff_in_charge
            services_names = department_data.pop("services", [])
            staff_in_charge_id = department_data.pop("staff_in_charge", None)
            if img:
                department_data["img"] = img

            # Create department
            department = Department.objects.create(
                organization=organization, **department_data
            )

            # Set staff in charge if provided
            if staff_in_charge_id:
                staff = get_object_or_404(Staff, id=staff_in_charge_id)
                department.staff_in_charge = staff
                department.save()

            # Add services
            for service_name in services_names:
                service, created = DepartmentService.objects.get_or_create(
                    name=service_name
                )
                department.services.add(service)

            return department
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{department_id}", response=DepartmentSchema, auth=JWTAuth()
    )
    def update_department(self, department_id: int, payload: UpdateDepartmentSchema, img: Optional[UploadedFile] = None):
        """Update a department"""
        department = get_object_or_404(Department, id=department_id)

        department_data = payload.model_dump(exclude_unset=True)

        # Handle services and staff_in_charge separately
        services_names = department_data.pop("services", None)
        staff_in_charge_id = department_data.pop("staff_in_charge", None)

        # Update basic fields
        for attr, value in department_data.items():
            setattr(department, attr, value)

        # Update staff in charge
        if staff_in_charge_id is not None:
            if staff_in_charge_id:
                staff = get_object_or_404(Staff, id=staff_in_charge_id)
                department.staff_in_charge = staff
            else:
                department.staff_in_charge = None
        if img:
            department.img = img  # type: ignore
        department.save()

        # Update services
        if services_names is not None:
            department.services.clear()
            for service_name in services_names:
                service, created = DepartmentService.objects.get_or_create(
                    name=service_name
                )
                department.services.add(service)

        return department

    @route.delete(
        "/{department_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_department(self, department_id: int):
        """Delete a department"""
        department = get_object_or_404(Department, id=department_id)
        department.delete()
        return {"message": "Department deleted successfully"}


@api_controller("/department-services", tags=["Department Services"])
class DepartmentServicesController:

    @route.get("/", response=DepartmentServiceListResponseSchema)
    def list_services(self):
        """Get all department services"""
        try:
            services = DepartmentService.objects.all().order_by("name")
            return {"services": list(services)}
        except Exception:
            return {"services": []}

    @route.post("/", response=DepartmentServiceSchema, auth=JWTAuth())
    def create_service(self, payload: CreateDepartmentServiceSchema):
        """Create a new department service"""
        try:
            service = DepartmentService.objects.create(**payload.model_dump())
            return service
        except Exception as e:
            return {"error": str(e)}

    @route.get("/{service_id}", response=DepartmentServiceSchema)
    def get_service(self, service_id: int):
        """Get a specific department service"""
        service = get_object_or_404(DepartmentService, id=service_id)
        return service

    @route.put(
        "/{service_id}", response=DepartmentServiceSchema, auth=JWTAuth()
    )
    def update_service(self, service_id: int, payload: UpdateDepartmentServiceSchema):
        """Update a department service"""
        service = get_object_or_404(DepartmentService, id=service_id)

        service_data = payload.model_dump(exclude_unset=True)
        for attr, value in service_data.items():
            setattr(service, attr, value)
        service.save()

        return service

    @route.delete(
        "/{service_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_service(self, service_id: int):
        """Delete a department service"""
        service = get_object_or_404(DepartmentService, id=service_id)
        service.delete()
        return {"message": "Department service deleted successfully"}
