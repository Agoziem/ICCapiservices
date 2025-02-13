from django.urls import path
from .views import authenticationviews, emailverificationviews, resetpasswordviews

urlpatterns = [
    path('register/', authenticationviews.register_user, name='register_user'),
    path('register_oauth/<str:provider>/', authenticationviews.register_user_with_oauth, name='register_user_with_oauth'),
    path('verifyuser/', authenticationviews.verify_user, name='verify_user'),
    path('getUsers/', authenticationviews.get_users, name='get_users'),
    path('getuser/<int:user_id>/', authenticationviews.get_user, name='get_user'),
    path('update/<int:user_id>/', authenticationviews.update_user, name='update_user'),
    path('delete/<int:user_id>/', authenticationviews.delete_user, name='delete_user'),
    
    path('getUserbyEmail/', emailverificationviews.get_user_by_email, name='get_verification_token_by_email'),
    path('verifyEmail/', emailverificationviews.verify_email, name='verify_email'),

    path('verifyToken/', resetpasswordviews.verify_token, name='verify_token'),
    path('resetPassword/', resetpasswordviews.reset_password, name='reset_password'),
    path('getResetPasswordToken/', resetpasswordviews.get_verification_token_by_email, name='get_verification_token_by_email'),
]