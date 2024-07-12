from django.urls import path
from .views import *

urlpatterns = [
    path('send-message/', send_whatsapp_message, name='send_message'),
    path('whatsapp-webhook/<str:token>/', whatsapp_webhook, name='whatsapp_webhook'),
]
