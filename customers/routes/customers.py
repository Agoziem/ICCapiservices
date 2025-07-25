from typing import Optional
from ninja_extra import api_controller, route
from ninja_extra.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ICCapp.models import Organization

from ..models import Customer
from ..schemas import (
    CustomerSchema,
    CustomerListResponseSchema,
    CreateCustomerSchema,
    UpdateCustomerSchema,
    SuccessResponseSchema,
    ErrorResponseSchema,
)


@api_controller("/customers", tags=["Customers"])
class CustomersController:

    @route.get("/{organization_id}", response=CustomerListResponseSchema)
    def list_customers(self, organization_id: int):
        """Get all customers for an organization"""
        try:
            customers = Customer.objects.filter(organization=organization_id)
            return {"customers": list(customers)}
        except Exception as e:
            return {"customers": []}

    @route.get("/customer/{customer_id}", response=CustomerSchema)
    def get_customer(self, customer_id: int):
        """Get a specific customer by ID"""
        customer = get_object_or_404(Customer, id=customer_id)
        return customer

    @route.post(
        "/{organization_id}", response=CustomerSchema, permissions=[IsAuthenticated]
    )
    def create_customer(self, organization_id: int, payload: CreateCustomerSchema):
        """Create a new customer for an organization"""
        try:
            organization = get_object_or_404(Organization, id=organization_id)
            customer_data = payload.model_dump()
            customer = Customer.objects.create(
                organization=organization, **customer_data
            )
            return customer
        except Exception as e:
            return {"error": str(e)}

    @route.put("/{customer_id}", response=CustomerSchema, permissions=[IsAuthenticated])
    def update_customer(self, customer_id: int, payload: UpdateCustomerSchema):
        """Update a customer"""
        customer = get_object_or_404(Customer, id=customer_id)

        customer_data = payload.model_dump(exclude_unset=True)
        for attr, value in customer_data.items():
            setattr(customer, attr, value)
        customer.save()

        return customer

    @route.delete(
        "/{customer_id}", response=SuccessResponseSchema, permissions=[IsAuthenticated]
    )
    def delete_customer(self, customer_id: int):
        """Delete a customer"""
        customer = get_object_or_404(Customer, id=customer_id)
        customer.delete()
        return {"message": "Customer deleted successfully"}
