from ..models import *
from ..serializers import ServiceSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from utils import get_full_image_url
from collections import Counter
from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()

class ServicePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

@swagger_auto_schema(
    method='get',
    operation_description="Get all users that have purchased a specific service",
    responses={
        200: "List of users that bought the service",
        404: "Service not found"
    }
)
@api_view(['GET'])
@permission_classes([])
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
                "avatar_url": get_full_image_url(user.avatar),
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
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve users'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='get',
    operation_description="Get all users whose service is currently in progress",
    responses={
        200: "List of users with in-progress services",
        404: "Service not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_users_whose_service_is_in_progress(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        users = service.userIDs_whose_services_is_in_progress.all()
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": get_full_image_url(user.avatar),
                "user_count": count,
                "date_joined": user.date_joined
            }
            for user, count in Counter(users).items()
        ]
        paginator = ServicePagination()
        paginated_data = paginator.paginate_queryset(user_data, request)
        return paginator.get_paginated_response(paginated_data)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve users'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@swagger_auto_schema(
    method='get',
    operation_description="Get all users whose service has been completed",
    responses={
        200: "List of users with completed services",
        404: "Service not found"
    }
)
@api_view(['GET'])
@permission_classes([])
def get_users_whose_service_is_completed(request, service_id):
    try:
        service = Service.objects.get(id=service_id)
        users = service.userIDs_whose_services_have_been_completed.all()
        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "avatar_url": get_full_image_url(user.avatar),
                "user_count": count,
                "date_joined": user.date_joined
            }
            for user, count in Counter(users).items()
        ]
        paginator = ServicePagination()
        paginated_data = paginator.paginate_queryset(user_data, request)
        return paginator.get_paginated_response(paginated_data)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve users'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Add a user to the in-progress list for a service",
    responses={
        200: "User successfully added to in-progress list",
        400: "User is already in completed services",
        404: "Service or User not found"
    }
)
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
                {'error': f'User {user_id} is already in completed services and cannot be added to in-progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if the user is already in the 'in-progress' list
        if service.userIDs_whose_services_is_in_progress.filter(id=user_id).exists():
            return Response(
                {'message': f'User {user_id} is already in in-progress services'},
                status=status.HTTP_200_OK
            )
        
        # Add the user to the 'in-progress' list
        service.userIDs_whose_services_is_in_progress.add(user)
        service.save()
        return Response(
            {'message': f'User {user_id} added to in-progress services'},
            status=status.HTTP_200_OK
        )

    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': f'User {user_id} not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to add user to in-progress'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='post',
    operation_description="Remove a user from the in-progress list for a service",
    responses={
        200: "User successfully removed from in-progress list",
        400: "User is not in in-progress services",
        404: "Service or User not found"
    }
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
        
        if service.userIDs_whose_services_is_in_progress.filter(id=user_id).exists():
            # Remove the user from the in-progress field
            service.userIDs_whose_services_is_in_progress.remove(user)
            service.save()

            return Response(
                {'message': f'User {user_id} removed from in-progress services'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': f'User {user_id} not in in-progress services'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': f'User {user_id} not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to remove user from in-progress'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    method='post',
    operation_description="Add a user to the completed services list",
    responses={
        200: "User successfully moved to completed services",
        404: "Service or User not found"
    }
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
            {'message': f'User {user_id} moved to completed services'},
            status=status.HTTP_200_OK
        )

    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': f'User {user_id} not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to add user to completed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@swagger_auto_schema(
    method='post',
    operation_description="Remove a user from the completed services list and add back to in-progress",
    responses={
        200: "User successfully removed from completed services",
        404: "Service or User not found"
    }
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
            {'message': f'User {user_id} removed from completed services'},
            status=status.HTTP_200_OK
        )
    
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': f'User {user_id} not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to remove user from completed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
