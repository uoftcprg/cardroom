from threading import Thread, Lock

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from cardroom.felt import Data
from cardroom.utilities import serialize

controller_lock = Lock()
controllers = {}
threads = {}


def get_controller(model):
    key = model.group_name

    with controller_lock:
        if key not in controllers:
            controllers[key] = model.load()
            threads[key] = Thread(target=controllers[key].mainloop)

            threads[key].start()

        return controllers[key]


def handle(model, user, content):
    get_controller(model).handle(user.username, content)


data_lock = Lock()
data = {}


def broadcast(model, data_=None):
    key = model.group_name

    if data_ is not None and data_:
        with data_lock:
            data[key] = data_[-1]

        async_to_sync(get_channel_layer().group_send)(
            model.group_name,
            {'type': 'data', 'data': serialize(data_)},
        )


def get_data(model):
    key = model.group_name

    with data_lock:
        return data.get(key, {'': Data()})
