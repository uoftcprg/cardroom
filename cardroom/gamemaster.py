from threading import Lock
from typing import ClassVar

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer  # type: ignore[import-untyped]

from cardroom.utilities import serialize
from cardroom.frame import Frame


class Gamemaster:
    _lock: ClassVar[Lock] = Lock()
    _frames: ClassVar[dict[str, dict[str, Frame]]] = {}

    @classmethod
    def broadcast(
            cls,
            group_name: str,
            frames: list[dict[str, Frame]],
            users_message: tuple[list[str], str],
    ) -> None:
        if frames:
            with cls._lock:
                cls._frames[group_name] = frames[-1]

            async_to_sync(get_channel_layer().group_send)(
                group_name,
                {'type': 'update', 'frames': serialize(frames)},
            )

        if all(users_message):
            users, message = users_message

            async_to_sync(get_channel_layer().group_send)(
                group_name,
                {'type': 'notify', 'users': users, 'message': message},
            )

    @classmethod
    def get_frames(cls, group_name: str) -> dict[str, Frame]:
        with cls._lock:
            return cls._frames[group_name]
