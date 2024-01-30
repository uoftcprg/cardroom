from threading import Thread, Lock

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from cardroom.utilities import serialize

controller_lock = Lock()
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
    with controller_lock:
        return controllers[model.group_name]


def handle(model, user, content):
    get_controller(model).handle(user.username, content)


data_lock = Lock()
data = {}


def broadcast(model, data_, user_message):
    if data_ is not None and data_:
        with data_lock:
            data[model.group_name] = data_[-1]

        async_to_sync(get_channel_layer().group_send)(
            model.group_name,
            {'type': 'data', 'data': serialize(data_)},
        )

    if user_message is not None:
        user, message = user_message

        async_to_sync(get_channel_layer().group_send)(
            model.group_name,
            {'type': 'message', 'user': user, 'message': message},
        )


def get_data(model):
    with data_lock:
        return data[model.group_name]
