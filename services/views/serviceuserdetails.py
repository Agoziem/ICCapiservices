from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from utils import get_full_image_url
from collections import Counter
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@api_view(['GET'])
def get_users_that_bought_service(request, service_id):
    try:
        # Get the service instance
        service = Service.objects.get(id=service_id)

        # Get the users that bought the service
        users = service.userIDs_that_bought_this_service.all()

        # Prepare the user data
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": get_full_image_url(user.avatar) ,
                "user_count": count,
                "date_joined": user.date_joined
            }
            for user, count in Counter(users).items()
        ]

        # Paginate the results
        paginator = ServicePagination()
        paginated_data = paginator.paginate_queryset(user_data, request)

        # Return paginated response
        return paginator.get_paginated_response(paginated_data)

    except Service.DoesNotExist:
        return Response({"detail": "Service not found."}, status=404)

@api_view(['GET'])
def get_users_whose_service_is_in_progress(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        users = service.userIDs_whose_services_is_in_progress.all()
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": get_full_image_url(user.avatar) ,
                "user_count": count,
                "date_joined": user.date_joined
            }
            for user, count in Counter(users).items()
        ]
        paginator = ServicePagination()
        paginated_data = paginator.paginate_queryset(user_data, request)
        return paginator.get_paginated_response(paginated_data)
    except Service.DoesNotExist:
        return Response({"detail": "Service not found."}, status=404)
    

@api_view(['GET'])
def get_users_whose_service_is_completed(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        users = service.userIDs_whose_services_have_been_completed.all()
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": get_full_image_url(user.avatar) ,
                "user_count": count,
                "date_joined": user.date_joined
            }
            for user, count in Counter(users).items()
        ]
        paginator = ServicePagination()
        paginated_data = paginator.paginate_queryset(user_data, request)
        return paginator.get_paginated_response(paginated_data)
    except Service.DoesNotExist:
        return Response({"detail": "Service not found."}, status=404)


@api_view(['POST'])
def add_user_to_in_progress(request, service_id, user_id):
    """
    Add the given user_id to the 'userIDs_whose_services_is_in_progress' field.
    """
    try:
        # Fetch the service and user objects
        service = Service.objects.get(id=service_id)
        user = User.objects.get(id=user_id)
        
        # Check if the user is in the 'completed' list
        if service.userIDs_whose_services_have_been_completed.filter(id=user_id).exists():
            return Response(
                {"message": f"User {user_id} is already in 'completed' services and cannot be added to 'in-progress'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the user is already in the 'in-progress' list
        if service.userIDs_whose_services_is_in_progress.filter(id=user_id).exists():
            return Response(
                {"message": f"User {user_id} is already in 'in-progress' services."},
                status=status.HTTP_200_OK
            )
        
        # Add the user to the 'in-progress' list
        service.userIDs_whose_services_is_in_progress.add(user)
        service.save()
        return Response(
            {"message": f"User {user_id} added to 'in-progress' services."},
            status=status.HTTP_200_OK
        )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    except User.DoesNotExist:
        return Response(
            {"error": f"User {user_id} not found."},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def remove_user_from_in_progress(request, service_id, user_id):
    """
    Remove the given user_id from the 'userIDs_whose_services_is_in_progress' field.
    """
    try:
        # Fetch the service by its ID
        service = Service.objects.get(id=service_id)
        user = User.objects.get(id=user_id)
        if service.userIDs_whose_services_is_in_progress.filter(id=user.id).exists():
            # Remove the user from the in-progress field
            service.userIDs_whose_services_is_in_progress.remove(user)
            service.save()

            return Response(
                {"message": f"User {user_id} removed from in-progress services."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": f"User {user_id} not in in-progress services."},
                status=status.HTTP_400_BAD_REQUEST  # Use 400 if it's a bad request
            )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    except User.DoesNotExist:
        return Response(
            {"error": f"User {user_id} not found."},
            status=status.HTTP_404_NOT_FOUND
        )



@api_view(['POST'])
def add_user_to_completed(request, service_id, user_id):
    """
    Add the given user_id to the 'userIDs_whose_services_have_been_completed' field.
    """
    try:
        service = Service.objects.get(id=service_id)
        user = User.objects.get(id=user_id)

        # Remove the user from 'in-progress' if present
        if service.userIDs_whose_services_is_in_progress.filter(id=user_id).exists():
            service.userIDs_whose_services_is_in_progress.remove(user)

        # Add the user to 'completed' if not already present
        if not service.userIDs_whose_services_have_been_completed.filter(id=user_id).exists():
            service.userIDs_whose_services_have_been_completed.add(user)

        service.save()  # Ensure the changes are persisted

        return Response(
            {"message": f"User {user_id} moved to completed services."},
            status=status.HTTP_200_OK
        )

    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    
@api_view(['POST'])
def remove_user_from_completed(request, service_id, user_id):
    """
    Remove the given user_id from the 'userIDs_whose_services_have_been_completed' field.
    """
    try:
        service = Service.objects.get(id=service_id)
        user = User.objects.get(id=user_id)
        if service.userIDs_whose_services_have_been_completed.filter(id=user_id).exists():
            service.userIDs_whose_services_have_been_completed.remove(user)

        if not service.userIDs_whose_services_is_in_progress.filter(id=user_id).exists():
            service.userIDs_whose_services_is_in_progress.add(user)
        service.save()
        return Response(
            {"message": f"User {user_id} removed from completed services."},
            status=status.HTTP_200_OK
        )
    
    except Service.DoesNotExist:
        return Response(
            {"error": "Service not found."},
            status=status.HTTP_404_NOT_FOUND
        )
