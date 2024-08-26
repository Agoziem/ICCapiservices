from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/whatsappapiSocket/', consumers.GeneralWhatsappConsumer.as_asgi()),
    path('ws/whatsappapiSocket/<str:contactwa_id>/', consumers.WhatsappConsumer.as_asgi()),
]
