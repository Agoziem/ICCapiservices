from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ninja_jwt.authentication import JWTAuth

from ..models import Organization, Subscription
from ..schemas import (
    SubscriptionSchema,
    SubscriptionListResponseSchema,
    CreateSubscriptionSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/subscriptions", tags=["Subscriptions"])
class SubscriptionsController:

    @route.get("/{organization_id}", response=SubscriptionListResponseSchema)
    def list_subscriptions(self, organization_id: int):
        """Get all subscriptions for an organization"""
        try:
            subscriptions = Subscription.objects.filter(
                organization=organization_id
            ).order_by("-date_added")
            return {"subscriptions": list(subscriptions)}
        except Exception:
            return {"subscriptions": []}

    @route.get("/subscription/{subscription_id}", response=SubscriptionSchema)
    def get_subscription(self, subscription_id: int):
        """Get a specific subscription by ID"""
        subscription = get_object_or_404(Subscription, id=subscription_id)
        return subscription

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
