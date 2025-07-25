from typing import List
from ninja_extra import api_controller, http_get, http_post, http_put, http_delete
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import Http404

from ..models import Comment, Blog
from ..schemas import (
    CommentSchema,
    CreateCommentSchema,
    UpdateCommentSchema,
    ErrorResponseSchema,
    SuccessResponseSchema,
    CommentListResponseSchema,
)

User = get_user_model()


@api_controller("/comments", tags=["Blog Comments"])
class CommentsController:

    @http_get(
        "/blog/{blog_id}", response={200: List[CommentSchema], 404: str, 500: str}
    )
    def get_blog_comments(self, blog_id: int):
        """Get all comments for a specific blog"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            comments = (
                Comment.objects.filter(blog=blog)
                .select_related("user")
                .order_by("-date")
            )
            return 200, [CommentSchema.model_validate(comment) for comment in comments]
        except Http404:
            return 404, "Blog not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_post(
        "/blog/{blog_id}/user/{user_id}",
        response={201: CommentSchema, 400: ErrorResponseSchema, 404: str, 500: str},
    )
    def create_comment(self, blog_id: int, user_id: int, data: CreateCommentSchema):
        """Create a new comment on a blog"""
        try:
            blog = get_object_or_404(Blog, id=blog_id)
            user = get_object_or_404(User, id=user_id)

            comment = Comment.objects.create(blog=blog, user=user, comment=data.comment)

            return 201, CommentSchema.model_validate(comment)

        except Http404 as e:
            return 404, str(e)
        except Exception as e:
            print(e)
            return 500, "Failed to create comment"

    @http_put("/{comment_id}", response={200: CommentSchema, 404: str, 500: str})
    def update_comment(self, comment_id: int, data: UpdateCommentSchema):
        """Update an existing comment"""
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment.comment = data.comment
            comment.save()
            return 200, CommentSchema.model_validate(comment)

        except Http404:
            return 404, "Comment not found"
        except Exception as e:
            print(e)
            return 500, "Failed to update comment"

    @http_delete("/{comment_id}", response={204: None, 404: str, 500: str})
    def delete_comment(self, comment_id: int):
        """Delete a comment"""
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            comment.delete()
            return 204, None
        except Http404:
            return 404, "Comment not found"
        except Exception as e:
            print(e)
            return 500, "Failed to delete comment"

    @http_get("/{comment_id}", response={200: CommentSchema, 404: str, 500: str})
    def get_comment(self, comment_id: int):
        """Get a specific comment by ID"""
        try:
            comment = get_object_or_404(Comment, id=comment_id)
            return 200, CommentSchema.model_validate(comment)
        except Http404:
            return 404, "Comment not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"

    @http_get(
        "/user/{user_id}", response={200: List[CommentSchema], 404: str, 500: str}
    )
    def get_user_comments(self, user_id: int):
        """Get all comments by a specific user"""
        try:
            user = get_object_or_404(User, id=user_id)
            comments = (
                Comment.objects.filter(user=user)
                .select_related("blog")
                .order_by("-date")
            )
            return 200, [CommentSchema.model_validate(comment) for comment in comments]
        except Http404:
            return 404, "User not found"
        except Exception as e:
            print(e)
            return 500, "Internal server error"
