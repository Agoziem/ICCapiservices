from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import *
from ICCapp.models import Organization
from django.contrib.auth import get_user_model
from ..serializers import *

User = get_user_model()

# --------------------------------------------------
# create a new chat group
# --------------------------------------------------
api_view(['POST'])
def create_groupchat(request,user_id):
    # get data from request
    data = request.data
    group_name = data.get('group_name', None)
    group_description = data.get('group_description', None)
    organization = data.get('organization', None)
    members = data.get('members', [])

    try:
        user = User.objects.get(id=user_id)
        organization = Organization.objects.get(id=organization)
        owner = user.id
        Admins = [owner]  # the owner of the chat group is an admin by default

        chat_group = ChatGroup.objects.create(
            group_name=group_name,
            group_description=group_description,
            owner=owner,
            admins = Admins,
            organization=organization,
        )
        chat_group.members.add(user)
        chat_group.members.add(*members) # add members to the chat group
        chat_group.save()
        serializer = ChatGroupSerializer(chat_group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# --------------------------------------------------
# edit chatroom
# --------------------------------------------------
@api_view(['PUT'])
def chatroom_edit_view(request, chatroom_id, user_id):
    data = request.data
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, admin__id=user_id)
        chatroom.group_name = data.get('group_name', chatroom.group_name)
        chatroom.group_description = data.get('group_description', chatroom.group_description)
        chatroom.save()
        serializer = ChatGroupSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
# --------------------------------------------------
# delete chatroom
# --------------------------------------------------
@api_view(['DELETE'])
def chatroom_delete_view(request, chatroom_id, user_id):
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, owner=user_id)
        chatroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    


# --------------------------------------------------
# add users to chatroom
# --------------------------------------------------
@api_view(['POST'])
def add_users_to_chatroom(request, chatroom_id, admin_id):
    data = request.data
    users = data.get('users', []) # list of user ids to add to the chatroom
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, admins__id=admin_id)
        chatroom.members.add(*users)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------
# add user to chatroom
# --------------------------------------------------
@api_view(['POST'])
def add_user_to_chatroom(request,chatroom_id, admin_id):
    user_id = request.data.get('user_id', None)
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id,admins__id=admin_id)
        chatroom.members.add(user_id)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    

# --------------------------------------------------
# remove members from chatroom
# --------------------------------------------------
@api_view(['DELETE'])
def remove_members_from_chatroom(request, chatroom_id, admin_id):
    data = request.data
    users = data.get('users', [])  # list of user IDs to remove from the chatroom

    try:
        # Retrieve the chatroom where the current user is an admin
        chatroom = ChatGroup.objects.get(id=chatroom_id, admins__id=admin_id)
        
        # Remove users from admins if they are in the list
        for user_id in users:
            if chatroom.admins.filter(id=user_id).exists():
                chatroom.admins.remove(user_id)
        
        # Remove users from members
        chatroom.members.remove(*users)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------
# remove member from chatroom
# --------------------------------------------------
@api_view(['DELETE'])
def remove_member_from_chatroom(request,chatroom_id, admin_id):
    user_id = request.data.get('user_id', None)
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, admins__id=admin_id)
        chatroom.members.remove(user_id)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)


# --------------------------------------------------
# add Admins to chatroom
# --------------------------------------------------
@api_view(['POST'])
def add_admins_to_chatroom(request, chatroom_id, owner_id):
    data = request.data
    users = data.get('users', []) # list of user ids to add as Admins to the chatroom
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, owner=owner_id)
        chatroom.admins.add(*users)
        chatroom.save()
        serializer = ChatGroupSerializer(chatroom)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)

# --------------------------------------------------
# add admin to chatroom
# --------------------------------------------------
@api_view(['POST'])
def add_admin_to_chatroom(request,chatroom_id, owner_id):
    user_id = request.data.get('user_id', None)
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, owner=owner_id)
        chatroom.admins.add(user_id)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)   

# --------------------------------------------------
# remove Admins from chatroom
# --------------------------------------------------
@api_view(['DELETE'])
def remove_admins_from_chatroom(request, chatroom_id, owner_id):
    data = request.data
    users = data.get('users', []) # list of user ids to remove as Admins from the chatroom
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, owner=owner_id)
        chatroom.admins.remove(*users)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
# --------------------------------------------------
# remove admin from chatroom
# --------------------------------------------------
@api_view(['DELETE'])
def remove_admin_from_chatroom(request,chatroom_id, owner_id):
    user_id = request.data.get('user_id', None)
    try:
        chatroom = ChatGroup.objects.get(id=chatroom_id, owner=owner_id)
        chatroom.admins.remove(user_id)
        chatroom.save()
        return Response(status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response({
            'error': 'Chatroom not found'
        }, status=status.HTTP_404_NOT_FOUND)

