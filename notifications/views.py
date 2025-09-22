from functools import partial
from typing import cast
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.http import QueryDict
from ICCapiservices.firebase import send_batch_notification
from authentication.serializers import SuccessResponseSerializer
from utils import normalize_img_field, parse_json_fields
from .models import NotificationModified, NotificationRecipient
from .serializers import (
    NotificationCreateSerializer,
    NotificationUpdateSerializer,
    NotificationReadUpdateSerializer,
    RemoveNotificationSerializer,
    NotificationResponseSerializer,
    NotificationOnlyResponseSerializer,
    UserNotificationListSerializer
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.models import CustomUser

User = cast(type[CustomUser], get_user_model())

# --------------------------------------------------------------------------
# Create notification
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="post",
    request_body=NotificationCreateSerializer,
    responses={
        201: SuccessResponseSerializer,
        400: 'Bad Request',
        404: 'User Not Found'
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def create_notification(request):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()
    else:
        data = request.data
        
    try:
        # Handle image field if present
        data = normalize_img_field(data, "image")
        parsed_data = parse_json_fields(data)
        print(f"Parsed data for notification creation: {parsed_data}")
        # Remove fields that need special handling
        user_ids = parsed_data.pop('user_ids', [])
        sender = parsed_data.pop('sender', None)

        # Set sender if provided
        sender = None
        if sender:
            sender = User.objects.get(id=sender)
        else:
            sender = User.objects.get(id=request.user.id)

        # Create the notification
        notification = NotificationModified.objects.create(
            sender=sender,
            **parsed_data
        )

        # Create recipients
        if user_ids:
            recipients_to_create = [
                NotificationRecipient(notification=notification, user_id=user_id, is_read=False)
                for user_id in user_ids
            ]
            NotificationRecipient.objects.bulk_create(recipients_to_create)
        else:
            # if no user_ids provided, send to all users
            all_user_ids = User.objects.values_list('id', flat=True)
            recipients_to_create = [
                NotificationRecipient(notification=notification, user_id=user_id, is_read=False)
                for user_id in all_user_ids
            ]
            NotificationRecipient.objects.bulk_create(recipients_to_create)
            user_ids = list(all_user_ids)  # For sending notifications to all users
        
        # Publish via Firebase push notification
        users = CustomUser.objects.filter(id__in=user_ids).exclude(fcmToken__isnull=True).exclude(fcmToken__exact='')
        users_fcm_tokens = [user.fcmToken for user in users if user.fcmToken]
        message = {
            "tokens": users_fcm_tokens,
            "title": notification.title,
            "body": notification.message,
            "link": notification.link if notification.link else None
        }

        print(f"Sending notification to tokens: {users_fcm_tokens}")
        print(f"Notification message: {message}")

        # Send notification in the background
        send_batch_notification(**message)

        return Response({"message": "Notification sent successfully to all recipients"}, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({'error': 'Sender user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to create notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get unread notifications for a user
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="get",
    operation_description="Get all unread notifications for a specific user",
    responses={
        200: UserNotificationListSerializer(many=True),
        404: 'User Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_unread_notifications(request, user_id):
    try:
        # Validate user exists
        user = User.objects.get(id=user_id)
        
        # Get unread notifications for the user
        unread_notifications = NotificationRecipient.objects.filter(
            user=user,
            is_read=False
        ).select_related('notification', 'notification__sender').order_by('-notification__created_at')
        
        serializer = UserNotificationListSerializer(unread_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve unread notifications'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Mark notification as read
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="post",
    request_body=NotificationReadUpdateSerializer,
    responses={
        200: 'Notification marked as read',
        400: 'Bad Request',
        404: 'Notification or User Not Found'
    }
)
@api_view(['POST'])
def mark_notification_as_read(request):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()
    else:
        data = request.data
        
    try:
        parsed_data = parse_json_fields(data)
        serializer = NotificationReadUpdateSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        
        # Update the notification recipient
        recipient = NotificationRecipient.objects.get(
            notification_id=validated_data['notification_id'],
            user_id=validated_data['user_id']
        )
        recipient.is_read = validated_data['is_read']
        recipient.save()
        return Response({'message': 'Notification read status updated'}, status=status.HTTP_200_OK)
        
    except NotificationRecipient.DoesNotExist:
        return Response({'error': 'Notification recipient not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update notification read status'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get user sent notifications
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="get",
    operation_description="Get all notifications sent by a specific user",
    responses={
        200: NotificationResponseSerializer(many=True),
        404: 'User Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_user_sent_notifications(request, user_id):
    try:
        # Validate user exists
        user = User.objects.get(id=user_id)
        
        # Get notifications sent by the user
        sent_notifications = NotificationModified.objects.filter(
            sender=user
        ).prefetch_related('notificationrecipient_set__user').order_by('-created_at')
        
        serializer = NotificationResponseSerializer(sent_notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve sent notifications'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get all notifications
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="get",
    operation_description="Get all notifications in the system",
    responses={
        200: NotificationResponseSerializer(many=True),
        500: 'Internal Server Error'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_all_notifications(request):
    try:
        notifications = NotificationModified.objects.all().prefetch_related(
            'notificationrecipient_set__user'
        ).order_by('-created_at')
        
        serializer = NotificationResponseSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': 'Failed to retrieve notifications'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Get notification by ID
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="get",
    operation_description="Get a specific notification by its ID",
    responses={
        200: NotificationResponseSerializer,
        404: 'Notification Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def get_notification_by_id(request, notification_id):
    try:
        notification = NotificationModified.objects.prefetch_related(
            'notificationrecipient_set__user'
        ).get(id=notification_id)
        
        serializer = NotificationResponseSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except NotificationModified.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to retrieve notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Remove user from notification
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="post",
    request_body=RemoveNotificationSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: 'Bad Request',
        404: 'Notification recipient not found'
    }
)
@api_view(['POST'])
def remove_user_from_notification(request):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()
    else:
        data = request.data
        
    try:
        parsed_data = parse_json_fields(data)
        serializer = RemoveNotificationSerializer(data=parsed_data)
        serializer.is_valid(raise_exception=True)
        
        # Remove the notification recipient relationship
        recipient = NotificationRecipient.objects.get(
            notification_id=serializer.validated_data['notification_id'],
            user_id=serializer.validated_data['user_id']
        )
        recipient.delete()
        return Response(SuccessResponseSerializer({'message': 'User removed from notification'}).data, status=status.HTTP_200_OK)

    except NotificationRecipient.DoesNotExist:
        return Response({'error': 'Notification recipient not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to remove user from notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Update notification
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="put",
    request_body=NotificationUpdateSerializer,
    responses={
        200: SuccessResponseSerializer,
        400: 'Bad Request',
        404: 'Notification Not Found'
    }
)
@api_view(['PUT'])
@parser_classes([MultiPartParser, FormParser])
def update_notification(request, notification_id):
    if isinstance(request.data, QueryDict):
        data = request.data.copy()
    else:
        data = request.data
        
    try:
        notification = NotificationModified.objects.get(id=notification_id)
        
        # Handle image field if present
        data = normalize_img_field(data, "image")
        parsed_data = parse_json_fields(data)
        
        # Add notification ID to the data
        parsed_data['id'] = notification_id
        
        # Remove fields that need special handling
        removed_user_ids = parsed_data.pop('user_ids', [])
        removed_sender_id = parsed_data.pop('sender_id', None)
        
        # Update notification fields
        for field, value in parsed_data.items():
            if field != 'id':  # Don't update the ID
                setattr(notification, field, value)
        
        # Update sender if provided
        if removed_sender_id is not None:
            if removed_sender_id:
                sender = User.objects.get(id=removed_sender_id)
                notification.sender = sender
            else:
                notification.sender = None
        
        notification.save()
        
        # Update recipients if user_ids provided
        if removed_user_ids:
            # Remove existing recipients
            NotificationRecipient.objects.filter(notification=notification).delete()
            
            # Add new recipients
            recipients_to_create = [
                NotificationRecipient(notification=notification, user_id=user_id, is_read=False)
                for user_id in removed_user_ids
            ]
            NotificationRecipient.objects.bulk_create(recipients_to_create)
        
        # Publish via Firebase push notification
        users = CustomUser.objects.filter(id__in=removed_user_ids).exclude(fcmToken__isnull=True).exclude(fcmToken__exact='')
        users_fcm_tokens = [user.fcmToken for user in users if user.fcmToken]
        message = {
            "tokens": users_fcm_tokens,
            "title": notification.title,
            "body": notification.message,
            "link": notification.link if notification.link else None
        }

        print(f"Sending notification to tokens: {users_fcm_tokens}")
        print(f"Notification message: {message}")

        # Send notification in the background
        send_batch_notification(**message)

        return Response(SuccessResponseSerializer({'message': 'Notification updated successfully'}).data, status=status.HTTP_200_OK)

    except NotificationModified.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    except User.DoesNotExist:
        return Response({'error': 'Sender user not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to update notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------------------------------------------------------
# Delete notification
# --------------------------------------------------------------------------
@swagger_auto_schema(
    method="delete",
    operation_description="Delete a notification and all its recipients",
    responses={
        204: 'No Content - Notification deleted',
        404: 'Notification Not Found'
    }
)
@api_view(['DELETE'])
def delete_notification(request, notification_id):
    try:
        notification = NotificationModified.objects.get(id=notification_id)
        # Delete notification (this will cascade delete recipients too)
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    except NotificationModified.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': 'Failed to delete notification'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

