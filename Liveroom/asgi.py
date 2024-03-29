"""
ASGI config for Liveroom project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""


import os

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Liveroom.settings')
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from Classes.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application


django.setup()

from .middleware import WebSocketAuthMiddleware,TokenAuthMiddlewareStack


application = ProtocolTypeRouter({    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    )
})


# application = ProtocolTypeRouter({
#   "http": get_asgi_application(),
#   "websocket": AuthMiddlewareStack(
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })
