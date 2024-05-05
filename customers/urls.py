from django.urls import path
from .views import *

urlpatterns = [
    path('customer/<int:organization_id>/', getCustomers, name='get_customers'),
    path('customer/<int:customer_id>/', getCustomer, name='get_customer'),
    path('customer/add/<int:organization_id>/', createCustomer, name='create_customer'),
    path('customer/update/<int:customer_id>/', updateCustomer, name='update_customer'),
    path('customer/delete/<int:customer_id>/', deleteCustomer, name='delete_customer'),
]