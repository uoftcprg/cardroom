# from collections.abc import Callable
# from datetime import datetime, timedelta
# from threading import Thread
# from time import sleep
# from typing import Any, ClassVar
# from unittest import TestCase
# from unittest.mock import MagicMock
#
# from pokerkit import (
#     BettingStructure,
#     Deck,
#     Opening,
#     Operation,
#     StandardHighHand,
#     Street,
# )
#
# from cardroom.table import Table
#
#
# class TableTestCase(TestCase):
#     SLEEP_MULTIPLIER: ClassVar[int] = 10
#
#     def create_table(
#             self,
#             callback: Callable[[Table, Operation | None], Any],
#     ) -> Table:
#         return Table(
#             6,
#             True,
#             Deck.STANDARD,
#             (StandardHighHand,),
#             (
#                 Street(
#                     False,
#                     (False,) * 2,
#                     0,
#                     False,
#                     Opening.POSITION,
#                     1,
#                     None,
#                 ),
#                 Street(
#                     True,
#                     (),
#                     3,
#                     False,
#                     Opening.POSITION,
#                     1,
#                     None,
#                 ),
#                 Street(
#                     True,
#                     (),
#                     1,
#                     False,
#                     Opening.POSITION,
#                     1,
#                     None,
#                 ),
#                 Street(
#                     True,
#                     (),
#                     1,
#                     False,
#                     Opening.POSITION,
#                     1,
#                     None,
#                 ),
#             ),
#             BettingStructure.NO_LIMIT,
#             True,
#             0,
#             (1, 2),
#             0,
#             180,
#             10,
#             3,
#             300,
#             0.1,
#             0.5,
#             0.25,
#             0.25,
#             0.25,
#             0.5,
#             20,
#             20,
#             20,
#             10,
#             3,
#             1,
#             0.5,
#             0.5,
#             1,
#             callback,
#         )
