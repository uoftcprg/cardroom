""":mod:`cardroom.tests.test_utilities` implements unit tests for
:mod:`cardroom.utilities`.
"""

from queue import Queue
from random import shuffle
from threading import Thread
from typing import ClassVar
from unittest import TestCase

from cardroom.utilities import Scheduler


class SchedulerTestCase(TestCase):
    STOP_VALUE: ClassVar[int] = 10

    def test_sleep_sort(self) -> None:
        scheduler = Scheduler()
        thread = Thread(target=scheduler.run)

        thread.start()

        queue = Queue[int]()
        values = list(range(self.STOP_VALUE))

        shuffle(values)

        for i in values:
            scheduler.schedule(i, queue.put, i)

        scheduler.schedule(self.STOP_VALUE, scheduler.stop)
        thread.join()

        values = []

        while not queue.empty():
            values.append(queue.get())

        self.assertSequenceEqual(values, range(self.STOP_VALUE))
