from importlib import import_module

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from cardroom.utilities import get_root_routingconf

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AuthMiddlewareStack(
            URLRouter(import_module(get_root_routingconf()).urlpatterns),
        )
    },
)
