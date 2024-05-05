from .views.blogsviews import *
from .views.commentsviews import *
from .views.likesviews import *
from django.urls import path

urlpatterns = [
    path('blogs/<int:user_id>/', get_blogs),
    path('blog/<int:blog_id>/', get_blog),
    path('addblog/<int:user_id>/', add_blog),
    path('updateblog/<int:blog_id>/', update_blog),
    path('deleteblog/<int:blog_id>/', delete_blog),

    path('addcomment/<int:blog_id>/<int:user_id>/', add_comment),
    path('updatecomment/<int:comment_id>/', update_comment),
    path('deletecomment/<int:comment_id>/', delete_comment),

    path('addlike/<int:blog_id>/<int:user_id>/', add_like),
    path('deletelike/<int:like_id>/', delete_like),
]