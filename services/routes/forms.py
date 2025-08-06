from typing import Optional, List, Any, Dict
from ninja_extra import api_controller, route, paginate
from ninja_extra.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth import get_user_model

from ..models import Service, ServiceForm, FormField, FormSubmission
from ..schemas import (
    ServiceFormSchema,
    CreateServiceFormSchema,
    UpdateServiceFormSchema,
    FormFieldSchema,
    CreateFormFieldSchema,
    UpdateFormFieldSchema,
    FormSubmissionSchema,
    CreateFormSubmissionSchema,
    UpdateFormSubmissionSchema,
    PaginatedServiceFormResponseSchema,
    PaginatedFormFieldResponseSchema,
    PaginatedFormSubmissionResponseSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)

User = get_user_model()


class FormPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000


@api_controller("/service-forms", tags=["Service Form Builder"])
class ServiceFormController:

    @route.get("/{service_id}/form", response=ServiceFormSchema)
    def get_service_form(self, service_id: int):
        """Get the form for a specific service"""
        service = get_object_or_404(Service, id=service_id)
        try:
            form = ServiceForm.objects.get(service=service)
            return ServiceFormSchema.model_validate(form)
        except ServiceForm.DoesNotExist:
            # Return empty form structure if no form exists
            return {
                "id": None,
                "title": "Service Application Form",
                "description": None,
                "is_active": True,
                "fields": [],
                "created_at": None,
                "updated_at": None,
            }

    @route.post("/{service_id}/form", response=ServiceFormSchema, auth=JWTAuth())
    def create_service_form(self, service_id: int, payload: CreateServiceFormSchema):
        """Create a form for a service"""
        try:
            service = get_object_or_404(Service, id=service_id)
            
            # Check if form already exists
            existing_form = ServiceForm.objects.filter(service=service).first()
            if existing_form:
                return {"error": "Form already exists for this service"}
            
            form_data = payload.model_dump()
            form = ServiceForm.objects.create(service=service, **form_data)
            
            return ServiceFormSchema.model_validate(form)
        except Exception as e:
            return {"error": str(e)}

    @route.put("/{service_id}/form", response=ServiceFormSchema, auth=JWTAuth())
    def update_service_form(self, service_id: int, payload: UpdateServiceFormSchema):
        """Update a service form"""
        try:
            service = get_object_or_404(Service, id=service_id)
            form = get_object_or_404(ServiceForm, service=service)
            
            form_data = payload.model_dump(exclude_unset=True)
            for attr, value in form_data.items():
                setattr(form, attr, value)
            form.save()
            
            return ServiceFormSchema.model_validate(form)
        except Exception as e:
            return {"error": str(e)}

    @route.delete("/{service_id}/form", response=SuccessResponseSchema, auth=JWTAuth())
    def delete_service_form(self, service_id: int):
        """Delete a service form"""
        try:
            service = get_object_or_404(Service, id=service_id)
            form = get_object_or_404(ServiceForm, service=service)
            form.delete()
            return {"message": "Service form deleted successfully"}
        except Exception as e:
            return {"error": str(e)}


@api_controller("/form-fields", tags=["Form Fields Management"])
class FormFieldController:

    @route.get("/{form_id}/fields", response=PaginatedFormFieldResponseSchema)
    @paginate(FormPagination)
    def get_form_fields(self, form_id: int):
        """Get all fields for a specific form"""
        form = get_object_or_404(ServiceForm, id=form_id)
        fields = FormField.objects.filter(form=form).order_by('order', 'created_at')
        
        field_list = []
        for field in fields:
            field_list.append(FormFieldSchema.model_validate(field))
        
        return field_list

    @route.get("/field/{field_id}", response=FormFieldSchema)
    def get_form_field(self, field_id: int):
        """Get a specific form field"""
        field = get_object_or_404(FormField, id=field_id)
        return FormFieldSchema.model_validate(field)

    @route.post("/{form_id}/fields", response=FormFieldSchema, auth=JWTAuth())
    def create_form_field(self, form_id: int, payload: CreateFormFieldSchema):
        """Create a new form field"""
        try:
            form = get_object_or_404(ServiceForm, id=form_id)
            
            field_data = payload.model_dump()
            field = FormField.objects.create(form=form, **field_data)
            
            return FormFieldSchema.model_validate(field)
        except Exception as e:
            return {"error": str(e)}

    @route.put("/field/{field_id}", response=FormFieldSchema, auth=JWTAuth())
    def update_form_field(self, field_id: int, payload: UpdateFormFieldSchema):
        """Update an existing form field"""
        try:
            field = get_object_or_404(FormField, id=field_id)
            
            field_data = payload.model_dump(exclude_unset=True)
            for attr, value in field_data.items():
                setattr(field, attr, value)
            field.save()
            
            return FormFieldSchema.model_validate(field)
        except Exception as e:
            return {"error": str(e)}

    @route.delete("/field/{field_id}", response=SuccessResponseSchema, auth=JWTAuth())
    def delete_form_field(self, field_id: int):
        """Delete a form field"""
        try:
            field = get_object_or_404(FormField, id=field_id)
            field.delete()
            return {"message": "Form field deleted successfully"}
        except Exception as e:
            return {"error": str(e)}

    @route.post("/{form_id}/fields/reorder", response=SuccessResponseSchema, auth=JWTAuth())
    def reorder_form_fields(self, form_id: int, field_orders: List[Dict[str, int]]):
        """Reorder form fields. Expects: [{"field_id": 1, "order": 0}, {"field_id": 2, "order": 1}]"""
        try:
            form = get_object_or_404(ServiceForm, id=form_id)
            
            for item in field_orders:
                field_id = item.get("field_id")
                order = item.get("order")
                if field_id and order is not None:
                    field = get_object_or_404(FormField, id=field_id, form=form)
                    field.order = order
                    field.save()
            
            return {"message": "Form fields reordered successfully"}
        except Exception as e:
            return {"error": str(e)}


@api_controller("/form-submissions", tags=["Form Submissions"])
class FormSubmissionController:

    @route.get("/{form_id}/submissions", response=PaginatedFormSubmissionResponseSchema, auth=JWTAuth())
    @paginate(FormPagination)
    def get_form_submissions(self, form_id: int):
        """Get all submissions for a specific form"""
        form = get_object_or_404(ServiceForm, id=form_id)
        submissions = FormSubmission.objects.filter(form=form).select_related('user').order_by('-submitted_at')
        
        submission_list = []
        for submission in submissions:
            # Create a temporary object with the required fields
            submission_data = type('SubmissionData', (), {
                'id': submission.pk,
                'submission_data': submission.submission_data,
                'submitted_at': submission.submitted_at,
                'updated_at': submission.updated_at,
                'user_id': submission.user.id,
                'username': submission.user.username,
            })()
            submission_list.append(submission_data)
        
        return submission_list

    @route.get("/submission/{submission_id}", response=FormSubmissionSchema, auth=JWTAuth())
    def get_form_submission(self, submission_id: int):
        """Get a specific form submission"""
        submission = get_object_or_404(FormSubmission.objects.select_related('user'), id=submission_id)
        
        # Create a temporary object with the required fields
        submission_data = type('SubmissionData', (), {
            'id': submission.pk,
            'submission_data': submission.submission_data,
            'submitted_at': submission.submitted_at,
            'updated_at': submission.updated_at,
            'user_id': submission.user.id,
            'username': submission.user.username,
        })()
        
        return submission_data

    @route.post("/{form_id}/submit", response=FormSubmissionSchema, auth=JWTAuth())
    def submit_form(self, request, form_id: int, payload: CreateFormSubmissionSchema):
        """Submit a form response"""
        try:
            form = get_object_or_404(ServiceForm, id=form_id)
            user = request.user
            
            # Check if user already submitted this form
            existing_submission = FormSubmission.objects.filter(form=form, user=user).first()
            if existing_submission:
                return {"error": "You have already submitted this form"}
            
            submission_data = payload.model_dump()
            submission = FormSubmission.objects.create(
                form=form,
                user=user,
                **submission_data
            )
            
            # Create a temporary object with the required fields
            response_data = type('SubmissionData', (), {
                'id': submission.pk,
                'submission_data': submission.submission_data,
                'submitted_at': submission.submitted_at,
                'updated_at': submission.updated_at,
                'user_id': submission.user.id,
                'username': submission.user.username,
            })()
            
            return response_data
        except Exception as e:
            return {"error": str(e)}

    @route.put("/submission/{submission_id}", response=FormSubmissionSchema, auth=JWTAuth())
    def update_form_submission(self, request, submission_id: int, payload: UpdateFormSubmissionSchema):
        """Update a form submission (only by the user who submitted it)"""
        try:
            submission = get_object_or_404(FormSubmission.objects.select_related('user'), id=submission_id, user=request.user)
            
            submission_data = payload.model_dump(exclude_unset=True)
            for attr, value in submission_data.items():
                setattr(submission, attr, value)
            submission.save()
            
            # Create a temporary object with the required fields
            response_data = type('SubmissionData', (), {
                'id': submission.pk,
                'submission_data': submission.submission_data,
                'submitted_at': submission.submitted_at,
                'updated_at': submission.updated_at,
                'user_id': submission.user.id,
                'username': submission.user.username,
            })()
            
            return response_data
        except Exception as e:
            return {"error": str(e)}

    @route.delete("/submission/{submission_id}", response=SuccessResponseSchema, auth=JWTAuth())
    def delete_form_submission(self, request, submission_id: int):
        """Delete a form submission (only by the user who submitted it)"""
        try:
            submission = get_object_or_404(FormSubmission, id=submission_id, user=request.user)
            submission.delete()
            return {"message": "Form submission deleted successfully"}
        except Exception as e:
            return {"error": str(e)}

    @route.get("/user/{service_id}/submission", response=FormSubmissionSchema, auth=JWTAuth())
    def get_user_submission(self, request, service_id: int):
        """Get current user's submission for a service form"""
        try:
            service = get_object_or_404(Service, id=service_id)
            form = get_object_or_404(ServiceForm, service=service)
            submission = get_object_or_404(FormSubmission.objects.select_related('user'), form=form, user=request.user)
            
            # Create a temporary object with the required fields
            response_data = type('SubmissionData', (), {
                'id': submission.pk,
                'submission_data': submission.submission_data,
                'submitted_at': submission.submitted_at,
                'updated_at': submission.updated_at,
                'user_id': submission.user.id,
                'username': submission.user.username,
            })()
            
            return response_data
        except FormSubmission.DoesNotExist:
            return {"error": "No submission found for this user"}
        except Exception as e:
            return {"error": str(e)}
