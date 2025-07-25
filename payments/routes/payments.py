from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg
from ninja_jwt.authentication import JWTAuth

from ICCapp.models import Organization
from services.models import Service
from products.models import Product
from vidoes.models import Video
from ..models import Orders
from ..Paystack import Paystack
from ..schemas import (
    OrderSchema,
    OrderListResponseSchema,
    CreateOrderSchema,
    UpdateOrderSchema,
    VerifyPaymentSchema,
    PaymentStatsSchema,
    PaymentVerificationResponseSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)

User = get_user_model()


@api_controller("/payments", tags=["Payments"])
class PaymentsController:

    @route.get("/{organization_id}", response=list[OrderSchema])
    def get_payments(self, organization_id: int):
        """Get all payments for an organization"""
        orders = (
            Orders.objects.filter(organization=organization_id)
            .select_related("organization", "customer")
            .prefetch_related("services", "products", "videos")
        )
        return orders

    @route.get("/user/{user_id}", response=list[OrderSchema])
    def get_payments_by_user(self, user_id: int):
        """Get all payments by a specific user"""
        orders = (
            Orders.objects.filter(customer=user_id)
            .select_related("organization", "customer")
            .prefetch_related("services", "products", "videos")
        )
        return orders

    @route.get("/order/{payment_id}", response=OrderSchema)
    def get_payment(self, payment_id: int):
        """Get a specific payment by ID"""
        order = get_object_or_404(
            Orders.objects.select_related("organization", "customer").prefetch_related(
                "services", "products", "videos"
            ),
            id=payment_id,
        )
        return order

    @route.post(
        "/{organization_id}", response=OrderSchema, auth=JWTAuth()
    )
    def add_payment(self, organization_id: int, payload: CreateOrderSchema):
        """Create a new payment order"""
        try:
            order_data = payload.model_dump()
            customer_id = order_data.pop("customerid")
            amount = order_data.pop("total")
            services_ids = order_data.pop("services", [])
            products_ids = order_data.pop("products", [])
            videos_ids = order_data.pop("videos", [])

            # Get related objects
            organization = get_object_or_404(Organization, id=organization_id)
            customer = get_object_or_404(User, id=customer_id)

            # Create order
            order = Orders.objects.create(
                organization=organization, customer=customer, amount=amount
            )

            # Add related items
            if services_ids:
                services = Service.objects.filter(id__in=services_ids)
                order.services.add(*services)

            if products_ids:
                products = Product.objects.filter(id__in=products_ids)
                order.products.add(*products)

            if videos_ids:
                videos = Video.objects.filter(id__in=videos_ids)
                order.videos.add(*videos)

            order.save()
            return order

        except Exception as e:
            return {"error": str(e)}

    @route.post("/verify", response=PaymentVerificationResponseSchema)
    def verify_payment(self, payload: VerifyPaymentSchema):
        """Verify a payment using Paystack"""
        try:
            reference = payload.reference
            customer_id = payload.customer_id

            if not reference:
                return {
                    "status": "error",
                    "message": "Reference is required",
                    "order": None,
                }

            paystack = Paystack()
            payment_status, data = paystack.verify_payment(reference)

            order = get_object_or_404(Orders, reference=reference)

            if payment_status:
                order.status = "Completed"

                # Update services
                for service in order.services.all():
                    service.number_of_times_bought += 1
                    service.userIDs_that_bought_this_service.add(customer_id)
                    if service.userIDs_whose_services_have_been_completed.filter(
                        id=customer_id
                    ).exists():
                        service.userIDs_whose_services_have_been_completed.remove(
                            customer_id
                        )
                    service.save()

                # Update products
                for product in order.products.all():
                    product.number_of_times_bought += 1
                    product.userIDs_that_bought_this_product.add(customer_id)
                    product.save()

                # Update videos
                for video in order.videos.all():
                    video.number_of_times_bought += 1
                    video.userIDs_that_bought_this_video.add(customer_id)
                    video.save()

                order.save()

                return {
                    "status": "success",
                    "message": "Payment verified successfully",
                    "order": order,
                }
            else:
                order.status = "Failed"
                order.save()

                return {
                    "status": "failed",
                    "message": "Payment verification failed",
                    "order": order,
                }

        except Exception as e:
            return {"status": "error", "message": str(e), "order": None}

    @route.put("/{payment_id}", response=OrderSchema, auth=JWTAuth())
    def update_payment(self, payment_id: int, payload: UpdateOrderSchema):
        """Update a payment order"""
        order = get_object_or_404(Orders, id=payment_id)

        try:
            order_data = payload.model_dump(exclude_unset=True)

            # Handle organization update
            if "organizationid" in order_data:
                organization_id = order_data.pop("organizationid")
                organization = get_object_or_404(Organization, id=organization_id)
                order.organization = organization

            # Handle customer update
            if "customerid" in order_data:
                customer_id = order_data.pop("customerid")
                customer = get_object_or_404(User, id=customer_id)
                order.customer = customer

            # Handle services update
            if "services" in order_data:
                services_ids = order_data.pop("services")
                order.services.clear()
                if services_ids:
                    services = Service.objects.filter(id__in=services_ids)
                    order.services.add(*services)

            # Handle products update
            if "products" in order_data:
                products_ids = order_data.pop("products")
                order.products.clear()
                if products_ids:
                    products = Product.objects.filter(id__in=products_ids)
                    order.products.add(*products)

            # Handle videos update
            if "videos" in order_data:
                videos_ids = order_data.pop("videos")
                order.videos.clear()
                if videos_ids:
                    videos = Video.objects.filter(id__in=videos_ids)
                    order.videos.add(*videos)

            # Update remaining fields
            for attr, value in order_data.items():
                setattr(order, attr, value)

            order.save()
            return order

        except Exception as e:
            return {"error": str(e)}

    @route.delete(
        "/{payment_id}", response=SuccessResponseSchema, auth=JWTAuth()
    )
    def delete_payment(self, payment_id: int):
        """Delete a payment order"""
        order = get_object_or_404(Orders, id=payment_id)
        order.delete()
        return {"message": "Payment deleted successfully"}

    @route.get("/stats/{organization_id}", response=PaymentStatsSchema)
    def get_payment_stats(self, organization_id: int):
        """Get payment statistics for an organization"""
        try:
            orders = Orders.objects.filter(organization=organization_id)
            customers = orders.values("customer__id", "customer__username").annotate(
                customer__count=Count("customer"),
                amount__sum=Sum("amount"),
                amount__avg=Avg("amount"),
            )

            total_orders = orders.count()
            total_customers = len(customers)

            customers_list = [
                {
                    "customer__id": customer["customer__id"],
                    "customer__username": customer["customer__username"],
                    "customer__count": customer["customer__count"],
                    "amount__sum": customer["amount__sum"],
                    "amount__avg": customer["amount__avg"],
                }
                for customer in customers
            ]

            return {
                "totalorders": total_orders,
                "totalcustomers": total_customers,
                "customers": customers_list,
            }

        except Exception as e:
            return {"totalorders": 0, "totalcustomers": 0, "customers": []}

    @route.post(
        "/{payment_id}/mark-delivered",
        response=OrderSchema,
        auth=JWTAuth(),
    )
    def mark_service_delivered(self, payment_id: int):
        """Mark service as delivered for a payment"""
        order = get_object_or_404(Orders, id=payment_id)
        order.service_delivered = True
        order.save()
        return order

    @route.get("/pending/{organization_id}", response=list[OrderSchema])
    def get_pending_payments(self, organization_id: int):
        """Get all pending payments for an organization"""
        orders = (
            Orders.objects.filter(organization=organization_id, status="Pending")
            .select_related("organization", "customer")
            .prefetch_related("services", "products", "videos")
        )
        return orders

    @route.get("/completed/{organization_id}", response=list[OrderSchema])
    def get_completed_payments(self, organization_id: int):
        """Get all completed payments for an organization"""
        orders = (
            Orders.objects.filter(organization=organization_id, status="Completed")
            .select_related("organization", "customer")
            .prefetch_related("services", "products", "videos")
        )
        return orders
