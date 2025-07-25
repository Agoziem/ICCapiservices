from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ICCapp.models import Organization, Subscription
from ninja_jwt.authentication import JWTAuth

from ..models import Email, EmailResponse, EmailMessage
from ..schemas import (
    EmailSchema,
    EmailListResponseSchema,
    CreateEmailSchema,
    UpdateEmailSchema,
    EmailResponseSchema,
    EmailResponseListSchema,
    CreateEmailResponseSchema,
    UpdateEmailResponseSchema,
    EmailMessageSchema,
    EmailMessageListSchema,
    CreateEmailMessageSchema,
    UpdateEmailMessageSchema,
    PaginatedEmailResponseSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/emails", tags=["Emails"])
class EmailsController:

    @route.get(
        "/subscriptions/{organization_id}", response=list[EmailListResponseSchema]
    )
    def get_subscriptions(self, organization_id: int):
        """Get all email subscriptions for an organization"""
        try:
            subscriptions = Subscription.objects.filter(organization=organization_id)
            return subscriptions
        except Exception:
            return []

    @route.get("/{organization_id}", response=PaginatedEmailResponseSchema)
    def get_emails(
        self,
        organization_id: int,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ):
        """Get all emails for an organization with pagination"""
        try:
            emails = Email.objects.filter(organization=organization_id).order_by(
                "-created_at"
            )
            if not page_size:
                page_size = 10
            paginator = Paginator(emails, page_size)
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

    @route.get("/email/{email_id}", response=EmailSchema)
    def get_email(self, email_id: int):
        """Get a specific email by ID"""
        email = get_object_or_404(Email, id=email_id)
        return email

    @route.post("/{organization_id}", response=EmailSchema)
    def add_email(self, organization_id: int, payload: CreateEmailSchema):
        """Create a new email and send websocket notification"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            email_data = payload.model_dump()

            email = Email.objects.create(organization=organization, **email_data)

            # Send WebSocket notification
            general_room_name = "emailapi"
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(  # type: ignore
                general_room_name,
                {
                    "type": "chat_message",
                    "operation": "create",
                    "contact": EmailSchema.model_validate(email).model_dump(),
                },
            )

            return email
        except Exception as e:
            return {"error": str(e)}

    @route.put("/{email_id}", response=EmailSchema, auth=JWTAuth())
    def update_email(self, email_id: int, payload: UpdateEmailSchema):
        """Update an email"""
        email = get_object_or_404(Email, id=email_id)

        email_data = payload.model_dump(exclude_unset=True)
        for attr, value in email_data.items():
            setattr(email, attr, value)
        email.save()

        return email

    @route.delete(
        "/{email_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_email(self, email_id: int):
        """Delete an email"""
        email = get_object_or_404(Email, id=email_id)
        email.delete()
        return {"message": "Email deleted successfully"}


@api_controller("/email-responses", tags=["Email Responses"])
class EmailResponsesController:

    @route.get("/{message_id}", response=EmailResponseListSchema)
    def get_responses(self, message_id: int):
        """Get all responses for a specific email message"""
        try:
            email = get_object_or_404(Email, id=message_id)
            responses = EmailResponse.objects.filter(message=email)
            return {"responses": list(responses)}
        except Exception:
            return {"responses": []}

    @route.post("/", response=EmailResponseSchema)
    def create_response(self, payload: CreateEmailResponseSchema):
        """Create a new email response"""
        try:
            response_data = payload.model_dump()
            response = EmailResponse.objects.create(**response_data)
            return response
        except Exception as e:
            return {"error": str(e)}

    @route.put(
        "/{response_id}", response=EmailResponseSchema, auth=JWTAuth()
    )
    def update_response(self, response_id: int, payload: UpdateEmailResponseSchema):
        """Update an email response"""
        response = get_object_or_404(EmailResponse, id=response_id)

        response_data = payload.model_dump(exclude_unset=True)
        for attr, value in response_data.items():
            setattr(response, attr, value)
        response.save()

        return response

    @route.delete(
        "/{response_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_response(self, response_id: int):
        """Delete an email response"""
        response = get_object_or_404(EmailResponse, id=response_id)
        response.delete()
        return {"message": "Email response deleted successfully"}


@api_controller("/email-messages", tags=["Email Messages"])
class EmailMessagesController:

    @route.get("/", response=EmailMessageListSchema)
    def get_sent_emails(self):
        """Get all sent email messages"""
        try:
            messages = EmailMessage.objects.all()
            return {"messages": list(messages)}
        except Exception:
            return {"messages": []}

    @route.post("/", response=EmailMessageSchema)
    def create_email_message(self, payload: CreateEmailMessageSchema):
        """Create a new email message"""
        try:
            message_data = payload.model_dump()
            message = EmailMessage.objects.create(**message_data, status="sent")
            return message
        except Exception as e:
            return {"error": str(e)}

    @route.get("/{message_id}", response=EmailMessageSchema)
    def get_email_message(self, message_id: int):
        """Get a specific email message"""
        message = get_object_or_404(EmailMessage, id=message_id)
        return message

    @route.put(
        "/{message_id}", response=EmailMessageSchema, auth=JWTAuth()
    )
    def update_email_message(self, message_id: int, payload: UpdateEmailMessageSchema):
        """Update an email message"""
        message = get_object_or_404(EmailMessage, id=message_id)

        message_data = payload.model_dump(exclude_unset=True)
        for attr, value in message_data.items():
            setattr(message, attr, value)
        message.save()

        return message

    @route.delete(
        "/{message_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_email_message(self, message_id: int):
        """Delete an email message"""
        message = get_object_or_404(EmailMessage, id=message_id)
        message.delete()
        return {"message": "Email message deleted successfully"}
