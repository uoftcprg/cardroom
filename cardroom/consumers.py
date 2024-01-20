from abc import ABC, abstractmethod
from typing import Any, ClassVar

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import AbstractUser

from cardroom.controller import CashGame, Controller


class ControllerConsumer(JsonWebsocketConsumer, ABC):
    group_name_prefix: ClassVar[str]

    @property
    def pk(self) -> int:
        return self.scope['url_route']['kwargs']['pk']

    @property
    def user(self) -> AbstractUser:
        return self.scope['user']

    @property
    def group_name(self) -> str:
        return self.group_name_prefix + str(self.pk)

    @property
    @abstractmethod
    def controller(self) -> Controller:
        pass

    def connect(self):
        super().connect()

        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name,
        )
        self.update()

    def disconnect(self, code) -> None:
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name,
        )

        super().disconnect(code)

    def receive_json(self, content: Any, **kwargs):
        # TODO: parse and apply content
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {'type': 'update', 'content': content},
        )

    def update(self, event: dict[str, Any] = None) -> None:
        # TODO: censor and send
        self.send_json(
            {
                'pk': self.pk,
                'user': self.user.username,
                'group_name': self.group_name,
                'event': event,
            },
        )


class CashGameConsumer(ControllerConsumer):
    group_name_prefix: ClassVar[str] = 'cash-game-'

    @property
    def controller(self) -> CashGame:
        pass  # TODO: get controller
