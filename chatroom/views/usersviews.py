
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ICCapp.models import Organization
from ..serializers import *


# --------------------------------------------------
# get all chat groups that belongs to an organization
# --------------------------------------------------
@api_view(['GET'])
def chat_list_view(request, organization_id):
    chat_groups = ChatGroup.objects.filter(organization=organization_id)
    serializer = ChatGroupSerializer(chat_groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --------------------------------------------------
# get all chat groups that a user is a member of
# --------------------------------------------------
@api_view(['GET'])
def chat_list_view(request, organization_id, user_id):
    chat_groups = ChatGroup.objects.filter(organization=organization_id, members__id=user_id)
    serializer = ChatGroupSerializer(chat_groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# --------------------------------------------------
# get a ChatGroup object by its id
# --------------------------------------------------
api_view(['GET'])
def chat_view(request, chatroom_id, user_id):
    try:
        chat_group = ChatGroup.objects.get(id=chatroom_id, members__id=user_id)
        serializer = ChatGroupSerializer(chat_group)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ChatGroup.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)