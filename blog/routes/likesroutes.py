from ninja_extra import api_controller, http_post, http_delete, http_get
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404

from ..models import Blog
from ..schemas import (
    LikeResponseSchema, ErrorResponseSchema, SuccessResponseSchema
)

User = get_user_model()


@api_controller('/likes', tags=['Blog Likes'])
class LikesController:
    
    @http_post('/blog/{blog_id}/user/{user_id}', response={200: LikeResponseSchema, 404: str, 500: str})
    def add_like(self, request, blog_id: int, user_id: int):
        """Add a like to a blog post"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            user = get_object_or_404(User, id=user_id)
            
            # Check if already liked
            if blog.likes.filter(id=user_id).exists():
                return 200, {
                    "liked": True,
                    "likes_count": blog.likes.count()
                }
            
            # Add like
            blog.likes.add(user)
            
            return 200, {
                "liked": True,
                "likes_count": blog.likes.count()
            }
            
        except Http404 as e:
            return 404, str(e)
        except Exception as e:
            print(e)
            return 500, "Failed to add like"

    @http_delete('/blog/{blog_id}/user/{user_id}', response={200: LikeResponseSchema, 404: str, 500: str})
    def remove_like(self, request, blog_id: int, user_id: int):
        """Remove a like from a blog post"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            user = get_object_or_404(User, id=user_id)
            
            # Check if actually liked
            if not blog.likes.filter(id=user_id).exists():
                return 200, {
                    "liked": False,
                    "likes_count": blog.likes.count()
                }
            
            # Remove like
            blog.likes.remove(user)
            
            return 200, {
                "liked": False,
                "likes_count": blog.likes.count()
            }
            
        except Http404 as e:
            return 404, str(e)
        except Exception as e:
            print(e)
            return 500, "Failed to remove like"

    @http_get('/blog/{blog_id}/user/{user_id}', response={200: LikeResponseSchema, 404: str, 500: str})
    def check_like_status(self, request, blog_id: int, user_id: int):
        """Check if a user has liked a specific blog"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            user = get_object_or_404(User, id=user_id)
            
            liked = blog.likes.filter(id=user_id).exists()
            
            return 200, {
                "liked": liked,
                "likes_count": blog.likes.count()
            }
            
        except Http404 as e:
            return 404, str(e)
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get('/blog/{blog_id}', response={200: dict, 404: str, 500: str})
    def get_blog_likes_count(self, request, blog_id: int):
        """Get the total number of likes for a blog"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            
            return 200, {
                "blog_id": blog_id,
                "likes_count": blog.likes.count()
            }
            
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"
