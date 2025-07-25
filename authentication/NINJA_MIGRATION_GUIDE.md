# Django Ninja Migration Guide for Authentication Module

## Overview
This migration converts the authentication module from Django REST Framework to django-ninja-extras, providing better performance, automatic OpenAPI documentation, and modern Python type hints.

## File Structure
```
authentication/
├── schema.py              # Ninja schemas (replaces serializers.py)
├── api.py                # Main API configuration
├── routes/               # Ninja controllers (replaces views/)
│   ├── __init__.py
│   ├── authenticationroutes.py
│   ├── passwordresetroutes.py
│   └── emailverificationroutes.py
├── ninja_urls.py         # New URL configuration
└── [existing files...]
```

## Key Changes

### 1. Serializers → Schemas
- `serializers.py` functionality moved to `schema.py`
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

### Authentication Routes (`/auth/`)
- `POST /auth/register` - Register new user
- `POST /auth/register-oauth/{provider}` - OAuth registration
- `POST /auth/verify` - Login/verify user
- `GET /auth/users` - Get all users
- `GET /auth/users/{user_id}` - Get user by ID
- `PUT /auth/users/{user_id}` - Update user
- `DELETE /auth/users/{user_id}` - Delete user

### Password Reset Routes (`/auth/password-reset/`)
- `POST /auth/password-reset/verify-token` - Verify reset token
- `POST /auth/password-reset/reset` - Reset password
- `POST /auth/password-reset/get-token` - Get reset token

### Email Verification Routes (`/auth/email-verification/`)
- `POST /auth/email-verification/verify` - Verify email
- `POST /auth/email-verification/get-user` - Get user for verification

## Usage Examples

### 1. Register User
```python
# Old DRF way
POST /authapi/register/
{
    "firstname": "John",
    "lastname": "Doe", 
    "email": "john@example.com",
    "password": "password123"
}

# New Ninja way
POST /authapi/ninja/auth/register
{
    "firstname": "John",
    "lastname": "Doe",
    "email": "john@example.com", 
    "password": "password123"
}
```

### 2. Update User (with file upload)
```python
# New Ninja way with file upload
PUT /authapi/ninja/auth/users/1
Content-Type: multipart/form-data

{
    "first_name": "John Updated",
    "avatar": <file>
}
```

## Migration Steps

### Step 1: Install Dependencies
```bash
pip install django-ninja-extras
```

### Step 2: Update URLs
Replace in `authentication/urls.py`:
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

### Step 3: Update Settings (if needed)
Add to `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'ninja_extra',
]
```

### Step 4: Test the API
Visit `/authapi/ninja/docs` for interactive API documentation.

## Benefits

1. **Automatic Documentation**: OpenAPI/Swagger docs generated automatically
2. **Type Safety**: Full Python type hints throughout
3. **Better Performance**: Faster than DRF
4. **Modern Python**: Uses Python 3.6+ features
5. **Validation**: Automatic request/response validation
6. **Error Handling**: Consistent error responses

## Response Format Examples

### Success Response
```json
{
    "token": "abc123...",
    "user": {
        "id": 1,
        "username": "john",
        "email": "john@example.com",
        "avatar_url": "https://example.com/media/avatars/avatar.jpg",
        // ... other fields
    }
}
```

### Error Response
```json
{
    "error": "User already exists"
}
```

## Notes

- File uploads handled via `ninja.File` and `UploadedFile`
- All endpoints maintain backward compatibility in terms of functionality
- Error responses are standardized across all endpoints
- Authentication/authorization can be added using ninja decorators
- The old DRF endpoints remain available during transition
