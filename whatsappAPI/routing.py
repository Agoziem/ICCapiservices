from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/whatsappapi/<str:contactwa_id>/', consumers.WhatsappConsumer.as_asgi()),
]
