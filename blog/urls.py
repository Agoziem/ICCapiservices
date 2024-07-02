from .views.blogsviews import *
from .views.commentsviews import *
from .views.likesviews import *
from django.urls import path

urlpatterns = [
    path('orgblogs/<int:organization_id>/', get_org_blogs),
    path('blogs/<int:user_id>/', get_blogs),
    path('blog/<int:blog_id>/', get_blog),
    path('blogbyslug/<slug:slug>/', get_blog_by_slug),
    path('addblog/<int:organization_id>/<int:user_id>/', add_blog),
    path('updateblog/<int:blog_id>/', update_blog),
    path('deleteblog/<int:blog_id>/', delete_blog),
    path('addviews/<int:blog_id>/', add_views),

    path('getCategories/', get_categories),
    path('addCategory/', add_category),
    path('updateCategory/<int:category_id>/', update_category),
    path('deleteCategory/<int:category_id>/', delete_category),

    path("getcomments/<int:blog_id>/", get_comments),
    path('addcomment/<int:blog_id>/<int:user_id>/', add_comment),
    path('updatecomment/<int:comment_id>/', update_comment),
    path('deletecomment/<int:comment_id>/', delete_comment),

    path('addlike/<int:blog_id>/<int:user_id>/', add_like),
    path('deletelike/<int:blog_id>/<int:user_id>/', delete_like),
]