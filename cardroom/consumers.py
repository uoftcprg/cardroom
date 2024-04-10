from abc import ABC, abstractmethod
from typing import Any, cast

from asgiref.sync import async_to_sync
from channels.generic.websocket import (  # type: ignore[import-untyped]
    JsonWebsocketConsumer,
)
from django.contrib.auth.models import AnonymousUser, User
from django.db import OperationalError, ProgrammingError

from cardroom.controllers import Controller
from cardroom.gamemaster import Gamemaster
from cardroom.models import CashGame
from cardroom.utilities import serialize
import cardroom.models as models


class ControllerConsumer(JsonWebsocketConsumer, ABC):  # type: ignore[misc]
    @classmethod
    @abstractmethod
    def setup(self) -> None:
        pass

    @property
    def pk(self) -> int:
        return cast(int, self.scope['url_route']['kwargs']['pk'])

    @property
    def user(self) -> AnonymousUser | User:
        return cast(AnonymousUser | User, self.scope['user'])

    @property
    @abstractmethod
    def controller(self) -> models.Controller:
        pass

    def connect(self) -> None:
        super().connect()

        group_name = self.controller.group_name

        async_to_sync(self.channel_layer.group_add)(
            group_name,
            self.channel_name,
        )
        self.update(
            {
                'type': 'update',
                'frames': [serialize(Gamemaster.get_frames(group_name))],
            },
        )

    def disconnect(self, code: int) -> None:
        async_to_sync(self.channel_layer.group_discard)(
            self.controller.group_name,
            self.channel_name,
        )
        super().disconnect(code)

    def receive_json(self, content: Any, **kwargs: Any) -> None:
        if self.user.is_authenticated:
            group_name = self.controller.group_name
            controller = Controller.lookup(group_name)

            controller.handle(self.user.username, content)
        else:
            self.notify(
                {
                    'type': 'notify',
                    'users': [''],
                    'message': 'You are not an authenticated user.',
                },
            )

    def update(self, event: dict[str, Any]) -> None:
        self.send_json(
            (
                event
                | {
                    'frames': [
                        frames.get(
                            self.user.username,
                            frames[''],
                        ) for frames in event['frames']
                    ],
                }
            )
        )

    def notify(self, event: dict[str, Any]) -> None:
        if self.user.username in event['users']:
            self.send_json(event)


class CashGameConsumer(ControllerConsumer):
    @classmethod
    def setup(self) -> None:
        try:
            cash_games = tuple(CashGame.objects.all())
        except (OperationalError, ProgrammingError):
            cash_games = ()

        for cash_game in cash_games:
            Controller.start(cash_game.group_name, cash_game.load())

    @property
    def controller(self) -> CashGame:
        return CashGame.objects.get(pk=self.pk)


CashGameConsumer.setup()
