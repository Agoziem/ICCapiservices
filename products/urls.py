from django.urls import path
from .views.productsviews import *
from .views.categoriesviews import *


urlpatterns = [
    path('products/<int:organization_id>/', get_products, name='get_products'),
    path('product/<int:product_id>/', get_product, name='get_product'),
    path('add-product/<int:organization_id>/', add_product, name='add_product'),
    path('update-product/<int:product_id>/', update_product, name='update_product'),
    path('delete-product/<int:product_id>/', delete_product, name='delete_product'),

    path('categories/', get_categories, name='get_categories'),
    path('add_category/', add_category, name='add_category'),
    path('update_category/<int:category_id>/', update_category, name='update_category'),
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),
]