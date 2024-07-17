from django.urls import path
from .views.categoriesviews import *
from .views.videoviews import *
from .views.subcategoriesviews import *

urlpatterns = [
    path('videos/<int:organization_id>/', get_videos, name='get_videos'),
    path('video/<int:video_id>/', get_video, name='get_video'),
    path('add_video/<int:organization_id>/', add_video, name='add_video'),
    path('update_video/<int:video_id>/', update_video, name='update_video'),
    path('delete_video/<int:video_id>/', delete_video, name='delete_video'),

    path('categories/', get_categories, name='get_categories'),
    path('add_category/', add_category, name='add_category'),
    path('update_category/<int:category_id>/', update_category, name='update_category'),
    path('delete_category/<int:category_id>/', delete_category, name='delete_category'),

    path('subcategories/<int:category_id>/', get_subcategories, name='get_subcategories'),
    path('subcategory/<int:subcategory_id>/', get_subcategory, name='get_subcategory'),
    path('create_subcategory/', create_subcategory, name='add_subcategory'),
    path('update_subcategory/<int:subcategory_id>/', update_subcategory, name='update_subcategory'),
    path('delete_subcategory/<int:subcategory_id>/', delete_subcategory, name='delete_subcategory'),
]