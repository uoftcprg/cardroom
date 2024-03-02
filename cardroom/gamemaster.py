from threading import Thread, Lock
from time import sleep

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import OperationalError, ProgrammingError

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


def mainloop():
    from cardroom.models import CashGame

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
