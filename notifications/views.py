from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from blog import serializers
from .models import NotificationModified as Notification
from .serializers import NotificationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_yasg.utils import swagger_auto_schema


# Fetch all notifications
@swagger_auto_schema(
    method="get",
    responses={
        200: NotificationSerializer(many=True),
        404: 'Notifications Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def fetch_notifications(request):
    notifications = Notification.objects.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Fetch a notification by its ID
@swagger_auto_schema(
    method="get",
    responses={
        200: NotificationSerializer(),
        404: 'Notification Not Found'
    }
)
@api_view(['GET'])
@permission_classes([])
def fetch_notification_by_id(request, id):
    try:
        notification = Notification.objects.get(id=id)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Create a new notification
@swagger_auto_schema(
    method="post",
    request_body=NotificationSerializer,
    responses={
        201: NotificationSerializer(),
        400: 'Bad Request'
    }
)
@api_view(['POST'])
def create_notification(request):
    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        # publish to websocket
        general_room_name = 'notifications'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            general_room_name,
            {
                'type': 'notification_message',
                'action':"add",
                'notification': serializer.data
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update an existing notification
@swagger_auto_schema(
    method="put",
    request_body=NotificationSerializer,
    responses={
        200: NotificationSerializer(),
        400: 'Bad Request',
        404: 'Notification Not Found'
    }
)
@api_view(['PUT'])
def update_notification(request, id):
    try:
        notification = Notification.objects.get(id=id)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = NotificationSerializer(notification, data=request.data)
    if serializer.is_valid():
        serializer.save()
        # publish to websocket
        general_room_name = 'notifications'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            general_room_name,
            {
                'type': 'notification_message',
                'action':"update",
                'notification': serializer.data
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a notification
@swagger_auto_schema(
    method="delete",
    responses={
        204: 'No Content',
        404: 'Notification Not Found'
    }
)
@api_view(['DELETE'])
def delete_notification(request, id):
    try:
        notification = Notification.objects.get(id=id)
        serialized_notification = NotificationSerializer(notification, many=False)
        print(serialized_notification)
        general_room_name = 'notifications'
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            general_room_name,
            {
                'type': 'notification_message',
                'action': "delete",
                'notification': serialized_notification.data  # serialized data with ID
            }
        )
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    notification.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)

