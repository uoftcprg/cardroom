from importlib import import_module

from channels.auth import AuthMiddlewareStack  # type: ignore[import-untyped]
from channels.routing import (  # type: ignore[import-untyped]
    ProtocolTypeRouter,
    URLRouter,
)
from channels.security.websocket import (  # type: ignore[import-untyped]
    AllowedHostsOriginValidator,
)
from django.core.asgi import get_asgi_application

from cardroom.middlewares import TokenAuthMiddlewareStack
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
