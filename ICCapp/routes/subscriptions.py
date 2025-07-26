from typing import List, Optional
from ninja_extra import api_controller, paginate, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import LimitOffsetPagination

from ..models import Organization, Subscription
from ..schemas import (
    SubscriptionSchema,
    SubscriptionListResponseSchema,
    CreateSubscriptionSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
    PaginatedSubscriptionResponseSchema,
)

class SubscriptionPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = "page_size"
    max_limit = 1000

@api_controller("/subscriptions", tags=["Subscriptions"])
class SubscriptionsController:

    @route.get("/{organization_id}", response=PaginatedSubscriptionResponseSchema)
    @paginate(SubscriptionPagination)
    def list_subscriptions(self, organization_id: int):
        """Get all subscriptions for an organization"""
        try:
            subscriptions = Subscription.objects.filter(
                organization=organization_id
            ).order_by("-date_added")
            return 200, subscriptions
        except Exception:
            return 500, {"error": "An error occurred while fetching subscriptions"}

    @route.get("/subscription/{subscription_id}", response={200: SubscriptionSchema, 404: str, 500: str})
    def get_subscription(self, subscription_id: int):
        """Get a specific subscription by ID"""
        subscription = get_object_or_404(Subscription, id=subscription_id)
        return 200, subscription

    @route.post("/{organization_id}", response=SubscriptionSchema)
    def create_subscription(
        self, organization_id: int, payload: CreateSubscriptionSchema
    ):
        """Create a new subscription"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)

            # Check if email already exists for this organization
            existing_subscription = Subscription.objects.filter(
                organization=organization, email=payload.email
            ).first()

            if existing_subscription:
                return existing_subscription

            subscription = Subscription.objects.create(
                organization=organization, email=payload.email
            )
            return subscription
        except Exception as e:
            return {"error": str(e)}

    @route.delete(
        "/{subscription_id}",
        response=SuccessResponseSchema,
        auth=JWTAuth(),
    )
    def delete_subscription(self, subscription_id: int):
        """Delete a subscription"""
        subscription = get_object_or_404(Subscription, id=subscription_id)
        subscription.delete()
        return {"message": "Subscription deleted successfully"}
