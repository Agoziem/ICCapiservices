from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

def get_tokens_for_user(user):
    """
    Generate JWT access and refresh tokens for a user
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh_token': str(refresh),
        'access_token': str(refresh.access_token),
    }

def create_jwt_response_data(user, message="Authentication successful"):
    """
    Create standardized JWT response data matching VerifyUserResponseSerializer
    """
    tokens = get_tokens_for_user(user)
    
    return {
        'message': message,
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
    }
