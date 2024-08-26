from django.urls import path
from .views.webhookviews import *
from .views.mediaviews import *
from .views.views import *

urlpatterns = [
    path('send-template-message/', send_whatsapp_message, name='send_message'),
    path('whatsapp-webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('messages/<int:contact_id>/', message_list, name='message_list'),
    path('contacts/', contact_list, name='contact_list'),
    path('media/<str:media_id>/', get_media, name='get_media'),
    path('<int:contact_id>/send_message/', send_to_whatsapp_api, name='send_to_whatsapp_api'),
]
# End of snippet from whatsappAPI/urls.py