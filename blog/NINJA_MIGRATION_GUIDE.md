# Django Ninja Migration Guide for Blog Module

## Overview
This migration converts the blog module from Django REST Framework to django-ninja-extras, providing better performance, automatic OpenAPI documentation, and modern Python type hints.

## File Structure
```
blog/
├── schemas.py            # Ninja schemas (replaces serializers.py)
├── api.py               # Main API configuration
├── routes/              # Ninja controllers (replaces views/)
│   ├── __init__.py
│   ├── blogsroutes.py
│   ├── categoriesroutes.py
│   ├── commentsroutes.py
│   └── likesroutes.py
├── ninja_urls.py        # New URL configuration
└── [existing files...]
```

## Key Changes

### 1. Serializers → Schemas
- `serializers.py` functionality moved to `schemas.py`
- Using `ninja.Schema` for input validation
- Using `ninja.ModelSchema` for model serialization
- Automatic type hints and validation

### 2. Views → Controllers
- Function-based views → Class-based controllers
- Automatic route registration
- Built-in response validation
- Better error handling

### 3. URL Configuration
- Centralized API configuration in `api.py`
- Controllers automatically register routes
- OpenAPI documentation auto-generated

## API Endpoints Mapping

### Blog Routes (`/blogs/`)
- `GET /blogs/` - Get all blogs (summary)
- `GET /blogs/organization/{organization_id}` - Get organization blogs
- `GET /blogs/user/{user_id}` - Get user blogs
- `GET /blogs/{blog_id}` - Get blog by ID (with comments)
- `GET /blogs/slug/{slug}` - Get blog by slug
- `POST /blogs/organization/{organization_id}/user/{user_id}` - Create blog
- `PUT /blogs/{blog_id}` - Update blog
- `DELETE /blogs/{blog_id}` - Delete blog
- `POST /blogs/{blog_id}/view` - Increment view count

### Category Routes (`/categories/`)
- `GET /categories/` - Get all categories
- `GET /categories/{category_id}` - Get category by ID
- `POST /categories/` - Create category
- `PUT /categories/{category_id}` - Update category
- `DELETE /categories/{category_id}` - Delete category

### Comment Routes (`/comments/`)
- `GET /comments/blog/{blog_id}` - Get blog comments
- `GET /comments/user/{user_id}` - Get user comments
- `GET /comments/{comment_id}` - Get comment by ID
- `POST /comments/blog/{blog_id}/user/{user_id}` - Create comment
- `PUT /comments/{comment_id}` - Update comment
- `DELETE /comments/{comment_id}` - Delete comment

### Like Routes (`/likes/`)
- `POST /likes/blog/{blog_id}/user/{user_id}` - Add like
- `DELETE /likes/blog/{blog_id}/user/{user_id}` - Remove like
- `GET /likes/blog/{blog_id}/user/{user_id}` - Check like status
- `GET /likes/blog/{blog_id}` - Get blog likes count

## Usage Examples

### 1. Create Blog Post
```python
# Old DRF way
POST /blogsapi/addBlog/1/1/
Content-Type: multipart/form-data
{
    "title": "My Blog Post",
    "subtitle": "A great post",
    "body": "<p>Blog content</p>",
    "category": 1,
    "tags": ["tech", "django"],
    "readTime": 5
}

# New Ninja way
POST /blogsapi/ninja/blogs/organization/1/user/1
Content-Type: multipart/form-data
{
    "title": "My Blog Post",
    "subtitle": "A great post", 
    "body": "<p>Blog content</p>",
    "category": 1,
    "tags": ["tech", "django"],
    "author": 1,
    "readTime": 5,
    "img": <file>
}
```

### 2. Get Blog with Comments
```python
# Old DRF way
GET /blogsapi/getBlog/1/

# New Ninja way
GET /blogsapi/ninja/blogs/1
```

### 3. Add/Remove Like
```python
# Old DRF way
POST /blogsapi/addLike/1/1/

# New Ninja way
POST /blogsapi/ninja/likes/blog/1/user/1
```

## Response Format Examples

### Blog Response
```json
{
    "id": 1,
    "title": "My Blog Post",
    "subtitle": "A great post",
    "body": "<p>Blog content</p>",
    "slug": "my-blog-post",
    "author": {
        "id": 1,
        "username": "author",
        "img": "https://example.com/avatar.jpg"
    },
    "category": {
        "id": 1,
        "category": "Technology",
        "description": "Tech posts"
    },
    "tags": [
        {"id": 1, "tag": "tech"},
        {"id": 2, "tag": "django"}
    ],
    "img_url": "https://example.com/blog_image.jpg",
    "img_name": "blog_image.jpg",
    "views": 150,
    "likes_count": 25,
    "date": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "readTime": 5,
    "comments": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "username": "commenter"
            },
            "comment": "Great post!",
            "date": "2024-01-15T11:00:00Z"
        }
    ],
    "comments_count": 1
}
```

### Like Response
```json
{
    "liked": true,
    "likes_count": 26
}
```

### Error Response
```json
{
    "error": "Blog not found"
}
```

## Migration Steps

### Step 1: Install Dependencies
```bash
pip install django-ninja-extras
```

### Step 2: Update URLs
Replace in `blog/urls.py`:
```python
from .ninja_urls import urlpatterns
```

Or to run both APIs side by side:
```python
from django.urls import path, include
from .ninja_urls import ninja_urlpatterns
from . import urls as old_urls

urlpatterns = [
    path('ninja/', include(ninja_urlpatterns)),
    path('', include(old_urls.urlpatterns)),
]
```

### Step 3: Test the API
Visit `/blogsapi/ninja/docs` for interactive API documentation.

## Benefits

1. **Automatic Documentation**: OpenAPI/Swagger docs generated automatically
2. **Type Safety**: Full Python type hints throughout
3. **Better Performance**: Faster than DRF
4. **File Upload Support**: Proper handling of blog image uploads
5. **Validation**: Automatic request/response validation
6. **Error Handling**: Consistent error responses
7. **Rich Text Support**: Maintains CKEditor rich text functionality

## Special Features

### 1. Automatic Slug Generation
When creating blogs, slugs are automatically generated from titles and made unique.

### 2. Tag Management
Tags are automatically created when referenced and can be reused across blogs.

### 3. Like System
Efficient like/unlike system with duplicate prevention.

### 4. View Tracking
Simple view counting system for blog analytics.

### 5. Rich Relationships
All responses include related data (author, category, tags, comments) in a single request.

## Notes

- File uploads handled via `ninja.File` and `UploadedFile`
- All endpoints maintain backward compatibility in terms of functionality
- Error responses are standardized across all endpoints
- The old DRF endpoints remain available during transition
- Slug generation ensures SEO-friendly URLs
- Rich text content from CKEditor is preserved
