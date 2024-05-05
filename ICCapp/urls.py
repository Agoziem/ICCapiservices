from django.urls import path
from .views import testimonialviews, staffviews, subscriptionviews, organizationviews

urlpatterns = [
    path('organization/', organizationviews.get_organizations, name='get_organizations'),
    path('organization/<int:organization_id>/', organizationviews.get_organization, name='get_organization'),
    path('organization/add/', organizationviews.add_organization, name='add_organization'),
    path('organization/update/<int:organization_id>/', organizationviews.update_organization, name='update_organization'),
    path('organization/delete/<int:organization_id>/', organizationviews.delete_organization, name='delete_organization'),
    
    path('testimonial/<int:organization_id>/', testimonialviews.get_testimonials, name='get_testimonials'),
    path('testimonial/<int:testimonial_id>/', testimonialviews.get_testimonial, name='get_testimonial'),
    path('testimonial/add/<int:organization_id>/', testimonialviews.add_testimonial, name='add_testimonial'),
    path('testimonial/update/<int:testimonial_id>/', testimonialviews.update_testimonial, name='update_testimonial'),
    path('testimonial/delete/<int:testimonial_id>/', testimonialviews.delete_testimonial, name='delete_testimonial'),
    
    path('staff/<int:organization_id>/', staffviews.get_staffs, name='get_staffs'),
    path('staff/<int:staff_id>/', staffviews.get_staff, name='get_staff'),
    path('staff/add/<int:organization_id>/', staffviews.add_staff, name='add_staff'),
    path('staff/update/<int:staff_id>/', staffviews.update_staff, name='update_staff'),
    path('staff/delete/<int:staff_id>/', staffviews.delete_staff, name='delete_staff'),
    
    path('subscription/<int:organization_id>/', subscriptionviews.get_subscriptions, name='get_subscriptions'),
    path('subscription/<int:subscription_id>/', subscriptionviews.get_subscription, name='get_subscription'),
    path('subscription/add/<int:organization_id>/', subscriptionviews.add_subscription, name='add_subscription'),
    path('subscription/update/<int:subscription_id>/', subscriptionviews.update_subscription, name='update_subscription'),
    path('subscription/delete/<int:subscription_id>/', subscriptionviews.delete_subscription, name='delete_subscription'),
]