from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Notification
from .serializers import NotificationSerializer

# Fetch all notifications
@api_view(['GET'])
def fetch_notifications(request):
    notifications = Notification.objects.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Fetch a notification by its ID
@api_view(['GET'])
def fetch_notification_by_id(request, id):
    try:
        notification = Notification.objects.get(id=id)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=status.HTTP_200_OK)

# # Create a new notification
# @api_view(['POST'])
# def create_notification(request):
#     serializer = NotificationSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Update an existing notification
# @api_view(['PUT'])
# def update_notification(request, id):
#     try:
#         notification = Notification.objects.get(id=id)
#     except Notification.DoesNotExist:
#         return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
#     serializer = NotificationSerializer(notification, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# # Delete a notification
# @api_view(['DELETE'])
# def delete_notification(request, id):
#     try:
#         notification = Notification.objects.get(id=id)
#     except Notification.DoesNotExist:
#         return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
#     notification.delete()
#     return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
