""":mod:`cardroom.utilities` implements classes related to cardroom
utilities.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from queue import Queue
from threading import Lock, Timer
from typing import Any, ClassVar, TypeAlias


@dataclass
class Scheduler:
    """The class for schedulers."""

    Event: ClassVar[TypeAlias] = Any
    _events: Queue[Event | None] = field(init=False, default_factory=Queue)
    _timers: dict[Event, Timer] = field(init=False, default_factory=dict)
    _lock: Lock = field(init=False, default_factory=Lock)

    def run(self) -> None:
        """Run the scheduler.

        :return: ``None``.
        """
        while (event := self._events.get()) is not None:
            event()
            self.cancel(event)

        with self._lock:
            timers = tuple(self._timers.values())

            self._timers.clear()

        for timer in timers:
            timer.cancel()

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
        event = partial(self._events.put, partial(function, *args, *kwargs))
        timer = Timer(timeout, event)

        with self._lock:
            self._timers[event] = timer

        timer.start()

        return event

    def cancel(self, event: Event) -> None:
        """Cancel an event.

        :param event: The event.
        :return: ``None``.
        """
        with self._lock:
            try:
                timer = self._timers.pop(event)
            except KeyError:
                timer = None

        if timer is not None:
            timer.cancel()
