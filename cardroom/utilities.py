""":mod:`cardroom.utilities` implements classes related to cardroom
utilities.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from queue import Queue
from threading import Timer
from typing import Any


@dataclass
class Scheduler:
    """The class for schedulers."""

    @dataclass
    class Event:
        """The class for events."""
        function: Callable[..., Any]
        """The funciton."""
        args: tuple[Any, ...]
        """The arguments."""
        kwargs: dict[str, Any]
        """The keyword arguments."""

    _events: Queue[Event | None] = field(init=False, default_factory=Queue)

    def run(self) -> None:
        """Run the scheduler.

        :return: ``None``.
        """
        while (event := self._events.get()) is not None:
            event.function(*event.args, **event.kwargs)

    def stop(self) -> None:
        """Stop the scheduler.

        :return: ``None``.
        """
        self._events.put(None)

    def schedule(
            self,
            timeout: float,
            function: Callable[..., Any],
            *args: Any,
            **kwargs: Any,
    ) -> Event:
        """Schedule an event.

        :param timeout: The timeout.
        :param function: The function.
        :param args: The arguments.
        :param kwargs: The keyword arguments.
        :return: The scheduled event.
        """
        event = self.Event(function, args, kwargs)
        timer = Timer(
            timeout,
            self._events.put,
            args=[event],
        )

        timer.start()

        return event
