from django.urls import path
from . import views

urlpatterns = [
    path('services/<int:organization_id>/', views.get_services, name='get_services'),
    path('service/<int:service_id>/', views.get_service, name='get_service'),
    path('add_service/<int:organization_id>/', views.add_service, name='add_service'),
    path('update_service/<int:service_id>/', views.update_service, name='update_service'),
    path('delete_service/<int:service_id>/', views.delete_service, name='delete_service'),
]