from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def message_list(request, contact_id):
    message = []
    sentmessages = SentMessage.objects.filter(contact_id=contact_id)
    recievedmessages = ReceivedMessage.objects.filter(contact_id=contact_id)
    sentmessages_serializer = SentMessageSerializer(sentmessages, many=True)
    recievedmessages_serializer = RecievedMessageSerializer(recievedmessages, many=True)
    message.extend(sentmessages_serializer.data)
    message.extend(recievedmessages_serializer.data)
    return Response(message, status=status.HTTP_200_OK)

@api_view(['GET'])
def contact_list(request):
    contacts = Contact.objects.all()
    serializer = ContactSerializer(contacts, many=True) 
    return Response(serializer.data, status=status.HTTP_200_OK)


