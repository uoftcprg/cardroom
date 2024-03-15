from abc import ABC, abstractmethod
from threading import Thread, Lock
from time import sleep

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer
from django.db import OperationalError, ProgrammingError

from cardroom.models import CashGame
from cardroom.utilities import get_gamemaster_timeout, serialize

controllers_lock = Lock()
controllers = {}
threads = {}


def set_controller(model):
    controllers[model.group_name] = model.load()
    threads[model.group_name] = Thread(
        target=controllers[model.group_name].mainloop,
        daemon=True,
    )

    threads[model.group_name].start()


def get_controller(model):
    with controllers_lock:
        return controllers[model.group_name]


def handle(model, user, content):
    get_controller(model).handle(user.username, content)


frames_lock = Lock()
frames = {}


def broadcast(model, sub_frames, users_message):
    if sub_frames is not None and sub_frames:
        with frames_lock:
            frames[model.group_name] = sub_frames[-1]

        async_to_sync(get_channel_layer().group_send)(
            model.group_name,
            {'type': 'update', 'frames': serialize(sub_frames)},
        )

    if all(users_message):
        users, message = users_message

        async_to_sync(get_channel_layer().group_send)(
            model.group_name,
            {'type': 'notify', 'users': users, 'message': message},
        )


def get_frames(model):
    with frames_lock:
        return frames[model.group_name]


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
        self.update(
            {
                'type': 'update',
                'frames': [serialize(get_frames(self.controller))],
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
            handle(self.controller, self.user, content)
        else:
            self.notify(
                {
                    'type': 'notify',
                    'users': [''],
                    'message': 'you are unauthenticated',
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


def mainloop():  # TODO: revert to signal based approach
    while True:
        try:
            for cash_game in CashGame.objects.all():
                try:
                    get_controller(cash_game)
                except KeyError:
                    set_controller(cash_game)
        except (OperationalError, ProgrammingError):
            pass

        sleep(get_gamemaster_timeout())


MAINLOOP_THREAD = Thread(target=mainloop, daemon=True)

MAINLOOP_THREAD.start()
