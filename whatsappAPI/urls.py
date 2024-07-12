from django.urls import path
from .views import *

urlpatterns = [
    path('send-message/', send_whatsapp_message, name='send_message'),
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
    path('reply_message/', reply_message, name='reply_message'),
    # path('get-messages/', get_messages, name='get_messages'),
    # path('get-contacts/<int:account_id>/', get_contacts, name='get_contacts'),
    # path('get-account/<int:account_id>/', get_accounts, name='get_accounts'),

]
