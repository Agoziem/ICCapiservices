from django.urls import path
from .views import servicesviews
from .views import categoriesviews
from .views.subcategoriesviews import *

urlpatterns = [
    path('services/<int:organization_id>/', servicesviews.get_services, name='get_services'),
    path('service/<int:service_id>/', servicesviews.get_service, name='get_service'),
    path('service_by_token/<str:servicetoken>/', servicesviews.get_service_token, name='get_service_token'),
    path('add_service/<int:organization_id>/', servicesviews.add_service, name='add_service'),
    path('update_service/<int:service_id>/', servicesviews.update_service, name='update_service'),
    path('delete_service/<int:service_id>/', servicesviews.delete_service, name='delete_service'),

    path('categories/', categoriesviews.get_categories, name='get_categories'),
    path('add_category/', categoriesviews.add_category, name='add_category'),
    path('update_category/<int:category_id>/', categoriesviews.update_category, name='update_category'),
    path('delete_category/<int:category_id>/', categoriesviews.delete_category, name='delete_category'),

    path('subcategories/<int:category_id>/', get_subcategories, name='get_subcategories'),
    path('subcategory/<int:subcategory_id>/', get_subcategory, name='get_subcategory'),
    path('create_subcategory/', create_subcategory, name='add_subcategory'),
    path('update_subcategory/<int:subcategory_id>/', update_subcategory, name='update_subcategory'),
    path('delete_subcategory/<int:subcategory_id>/', delete_subcategory, name='delete_subcategory'),
]