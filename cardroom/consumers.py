from abc import ABC, abstractmethod

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from cardroom.controller import Controller
from cardroom.gamemaster import Gamemaster
from cardroom.models import CashGame
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

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.controller.group_name,
            self.channel_name,
        )
        super().disconnect(code)

    def receive_json(self, content, **kwargs):
        if self.user.is_authenticated:
            group_name = self.controller.group_name

            Controller.get(group_name).handle(self.user, content)
        else:
            self.notify(
                {
                    'type': 'notify',
                    'users': [''],
                    'message': 'You are not an authenticated user.',
                },
            )

    def update(self, event):
        frames = []

        for sub_frames in event['frames']:
            frames.append(sub_frames.get(self.user.username, sub_frames['']))

        self.send_json(event | {'frames': frames})

    def notify(self, event):
        if self.user.username in event['users']:
            self.send_json(event)


class CashGameConsumer(ControllerConsumer):
    @property
    def controller(self):
        return CashGame.objects.get(pk=self.pk)
