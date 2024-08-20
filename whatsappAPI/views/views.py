from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import *
from ..serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def message_list(request, contact_id):
    messages = Message.objects.filter(contact_id=contact_id)
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def contact_list(request):
    contacts = Contact.objects.all()
    serializer = ContactSerializer(contacts, many=True) 
    return Response(serializer.data)


