from abc import ABC, abstractmethod

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from cardroom.models import CashGame
from cardroom.gamemaster import handle, get_data
from cardroom.utilities import serialize


class ControllerConsumer(JsonWebsocketConsumer, ABC):
    @property
    def pk(self):
        return self.scope['url_route']['kwargs']['pk']

    @property
    def user(self):
        return self.scope['user']

    @property
    @abstractmethod
    def controller(self):
        pass

    def connect(self):
        super().connect()
        async_to_sync(self.channel_layer.group_add)(
            self.controller.group_name,
            self.channel_name,
        )
        self.data(
            {'type': 'data', 'data': (serialize(get_data(self.controller)),)},
        )

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.controller.group_name,
            self.channel_name,
        )
        super().disconnect(code)

    def receive_json(self, content, **kwargs):
        if self.user.is_authenticated:
            handle(self.controller, self.user, content)
        else:
            self.message(
                {
                    'type': 'message',
                    'user': '',
                    'message': 'you are unauthenticated',
                },
            )

    def data(self, event):
        self.send_json(
            (
                event
                | {
                    'data': [
                        data.get(
                            self.user.username,
                            data[''],
                        ) for data in event['data']
                    ],
                }
            ),
        )

    def message(self, event):
        if (
                (self.user.is_anonymous and not event['user'])
                or (
                    self.user.is_authenticated
                    and event['user'] == self.user.username
                )
        ):
            self.send_json(event)


class CashGameConsumer(ControllerConsumer):
    @property
    def controller(self):
        return CashGame.objects.get(pk=self.pk)
