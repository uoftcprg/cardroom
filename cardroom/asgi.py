from importlib import import_module

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from cardroom.middleware import TokenAuthMiddlewareStack
from cardroom.utilities import get_root_routingconf

application = ProtocolTypeRouter(
    {
        'http': get_asgi_application(),
        'websocket': AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                TokenAuthMiddlewareStack(
                    URLRouter(
                        import_module(get_root_routingconf()).urlpatterns,
                    ),
                ),
            ),
        )
    },
)
