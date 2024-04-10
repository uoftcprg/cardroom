from typing import Any, cast

from urllib.parse import parse_qs

from channels.db import database_sync_to_async  # type: ignore[import-untyped]
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.authtoken.models import Token


@database_sync_to_async  # type: ignore[misc]
def get_user_from_token(token_key: str) -> AnonymousUser | User:
    try:
        return cast(User, Token.objects.get(key=token_key).user)
    except Token.DoesNotExist:
        return AnonymousUser()


class TokenAuthMiddleware:
    """The Token auth middleware for Django Channels."""

    def __init__(self, inner: Any) -> None:
        self.inner: Any = inner

    async def __call__(
            self,
            scope: dict[str, Any],
            receive: Any,
            send: Any,
    ) -> Any:
        query_string = parse_qs(scope['query_string'].decode())

        if 'token' in query_string:
            scope['user'] = await get_user_from_token(query_string['token'][0])
        elif 'user' not in scope:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)


def TokenAuthMiddlewareStack(inner: Any) -> TokenAuthMiddleware:
    return TokenAuthMiddleware(inner)
