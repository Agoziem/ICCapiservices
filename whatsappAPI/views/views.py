from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def message_list(request, contact_id):
    WAmessages = WAMessage.objects.filter(contact_id=contact_id)
    WAmessages_serializer = WAMessageSerializer(WAmessages, many=True)
    return Response(WAmessages_serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def contact_list(request):
    contacts = Contact.objects.all()
    serializer = ContactSerializer(contacts, many=True) 
    return Response(serializer.data, status=status.HTTP_200_OK)


