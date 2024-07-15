from django.urls import path
from .views import servicesviews
from .views import categoriesviews

urlpatterns = [
    path('services/<int:organization_id>/', servicesviews.get_services, name='get_services'),
    path('service/<int:service_id>/', servicesviews.get_service, name='get_service'),
    path('add_service/<int:organization_id>/', servicesviews.add_service, name='add_service'),
    path('update_service/<int:service_id>/', servicesviews.update_service, name='update_service'),
    path('delete_service/<int:service_id>/', servicesviews.delete_service, name='delete_service'),

    path('categories/', categoriesviews.get_categories, name='get_categories'),
    path('add_category/', categoriesviews.add_category, name='add_category'),
    path('update_category/<int:category_id>/', categoriesviews.update_category, name='update_category'),
    path('delete_category/<int:category_id>/', categoriesviews.delete_category, name='delete_category'),
]