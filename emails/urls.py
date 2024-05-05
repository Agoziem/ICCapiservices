from django.urls import path
from . import views

urlpatterns = [
    path('emails/<int:organization_id>/', views.get_emails, name='get_emails'),
    path('email/<int:email_id>/', views.get_email, name='get_email'),
    path('add_email/<int:organization_id>/', views.add_email, name='add_email'),
    path('update_email/<int:email_id>/', views.update_email, name='update_email'),
    path('delete_email/<int:email_id>/', views.delete_email, name='delete_email'),
]