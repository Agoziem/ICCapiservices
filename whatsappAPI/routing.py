from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/whatsappapiSocket/contacts/', consumers.WAContactsConsumer.as_asgi()),
    path('ws/whatsappapiSocket/messages/', consumers.WAMessagesConsumer.as_asgi()),
]
