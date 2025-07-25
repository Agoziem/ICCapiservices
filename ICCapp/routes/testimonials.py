from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from ..models import Organization, Testimonial
from ..schemas import (
    TestimonialSchema, TestimonialListResponseSchema, PaginatedTestimonialResponseSchema,
    CreateTestimonialSchema, UpdateTestimonialSchema,
    SuccessResponseSchema, ErrorResponseSchema
)


@api_controller('/testimonials', tags=['Testimonials'])
class TestimonialsController:
    
    @route.get('/{organization_id}', response=PaginatedTestimonialResponseSchema)
    def list_testimonials(self, organization_id: int, page: Optional[int] = 1, page_size: Optional[int] = 10):
        """Get all testimonials for an organization with pagination"""
        try:
            testimonials = Testimonial.objects.filter(organization=organization_id).order_by('-created_at')
            if not page_size:
                page_size = 10
            paginator = Paginator(testimonials, page_size)
            page_obj = paginator.get_page(page)
            
            return {
                "count": paginator.count,
                "next": f"?page={page_obj.next_page_number()}" if page_obj.has_next() else None,
                "previous": f"?page={page_obj.previous_page_number()}" if page_obj.has_previous() else None,
                "results": list(page_obj.object_list)
            }
        except Exception:
            return {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            }
    
    @route.get('/testimonial/{testimonial_id}', response=TestimonialSchema)
    def get_testimonial(self, testimonial_id: int):
        """Get a specific testimonial by ID"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        return testimonial
    
    @route.post('/{organization_id}', response=TestimonialSchema)
    def create_testimonial(self, organization_id: int, payload: CreateTestimonialSchema):
        """Create a new testimonial"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            testimonial_data = payload.model_dump()
            
            testimonial = Testimonial.objects.create(
                organization=organization,
                **testimonial_data
            )
            return testimonial
        except Exception as e:
            return {"error": str(e)}
    
    @route.put('/{testimonial_id}', response=TestimonialSchema, permissions=[IsAuthenticated])
    def update_testimonial(self, testimonial_id: int, payload: UpdateTestimonialSchema):
        """Update a testimonial"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        
        testimonial_data = payload.model_dump(exclude_unset=True)
        for attr, value in testimonial_data.items():
            setattr(testimonial, attr, value)
        testimonial.save()
        
        return testimonial
    
    @route.delete('/{testimonial_id}', response=SuccessResponseSchema, permissions=[IsAuthenticated])
    def delete_testimonial(self, testimonial_id: int):
        """Delete a testimonial"""
        testimonial = get_object_or_404(Testimonial, id=testimonial_id)
        testimonial.delete()
        return {"message": "Testimonial deleted successfully"}
