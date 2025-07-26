from typing import List, Optional
from ninja import UploadedFile
from ninja_extra import api_controller, route,paginate
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import LimitOffsetPagination



from ..models import Organization, Testimonial
from ..schemas import (
    TestimonialSchema,
    TestimonialListResponseSchema,
    CreateTestimonialSchema,
    UpdateTestimonialSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
    PaginatedTestimonialResponseSchema,
)

class TestimonialPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/testimonials", tags=["Testimonials"])
class TestimonialsController:

    @route.get("/{organization_id}", response=PaginatedTestimonialResponseSchema)
    @paginate(TestimonialPagination)
    def list_testimonials(
        self,
        organization_id: int,
    ):
        """Get all testimonials for an organization with pagination"""
        try:
            testimonials = Testimonial.objects.filter(
                organization=organization_id
            ).order_by("-created_at")
            return testimonials
        except Exception:
            return {"error": "An error occurred while fetching testimonials"}

    @route.get("/testimonial/{testimonial_id}", response=TestimonialSchema)
    def get_testimonial(self, testimonial_id: int):
        """Get a specific testimonial by ID"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        return testimonial

    @route.post("/{organization_id}", response=TestimonialSchema)
    def create_testimonial(
        self, organization_id: int, payload: CreateTestimonialSchema, img: Optional[UploadedFile] = None
    ):
        """Create a new testimonial"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            testimonial_data = payload.model_dump()
            if img:
                testimonial_data["img"] = img

            testimonial = Testimonial.objects.create(
                organization=organization, **testimonial_data
            )
            return testimonial
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{testimonial_id}", response=TestimonialSchema, auth=JWTAuth()
    )
    def update_testimonial(self, testimonial_id: int, payload: UpdateTestimonialSchema, img: Optional[UploadedFile] = None):
        """Update a testimonial"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)

        testimonial_data = payload.model_dump(exclude_unset=True)
        for attr, value in testimonial_data.items():
            setattr(testimonial, attr, value)

        if img:
            testimonial.img = img  # type: ignore
        testimonial.save()
        return testimonial

    @route.delete(
        "/{testimonial_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_testimonial(self, testimonial_id: int):
        """Delete a testimonial"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.delete()
        return {"message": "Testimonial deleted successfully"}
