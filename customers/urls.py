from django.urls import path
from .views import *

urlpatterns = [
    path('customers/', getCustomers, name='getCustomers'),
    path('customer/<int:pk>/', getCustomer, name='getCustomer'),
    path('customer/', createCustomer, name='createCustomer'),
    path('customer/<int:pk>/', updateCustomer, name='updateCustomer'),
    path('customer/<int:pk>/', deleteCustomer, name='deleteCustomer'),
]