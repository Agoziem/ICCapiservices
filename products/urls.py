from django.urls import path
from .views import *


urlpatterns = [
    path('products/<int:organization_id>/', get_products, name='get_products'),
    path('product/<int:product_id>/', get_product, name='get_product'),
    path('add-product/<int:organization_id>/', add_product, name='add_product'),
    path('update-product/<int:product_id>/', update_product, name='update_product'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),
]