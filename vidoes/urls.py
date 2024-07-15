from django.urls import path
from .views.categoriesviews import *
from .views.videoviews import *

urlpatterns = [
    path('videos/<int:organization_id>/', get_videos, name='get_videos'),
    path('video/<int:service_id>/', get_video, name='get_video'),
    path('add_video/<int:organization_id>/', add_video, name='add_video'),
    path('update_video/<int:service_id>/', update_video, name='update_video'),
    path('delete_video/<int:service_id>/', delete_video, name='delete_video'),

    path('categories/', get_categories, name='get_categories'),
    path('add_category/', add_category, name='add_category'),
    path('update_category/<int:category_id>/', update_category, name='update_category'),
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),
]