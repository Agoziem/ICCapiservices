from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/emailapiSocket/', consumers.EmailConsumer.as_asgi()),
]
