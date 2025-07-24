import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ICCapiservices.settings')

django_asgi_app = get_asgi_application()

from whatsappAPI import routing as whatsappAPI_routing
from notifications import routing as notifications_routing
from emails import routing as email_routing

application = ProtocolTypeRouter({
  "http": django_asgi_app,
  "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                whatsappAPI_routing.websocket_urlpatterns +
                email_routing.websocket_urlpatterns +
                notifications_routing.websocket_urlpatterns
            )
        )
    ),
})