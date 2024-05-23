from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('register_oauth/<str:provider>/', views.register_user_with_oauth, name='register_user_with_oauth'),
    path('verifyuser/', views.verify_user, name='verify_user'),
    path('update/<int:user_id>/', views.update_user, name='update_user'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
]