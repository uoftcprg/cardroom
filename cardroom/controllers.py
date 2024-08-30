""":mod:`cardroom.table` implements classes related to poker tables.

This module implements logic to control tables in real-time.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Empty, Queue
from threading import RLock, Thread
from traceback import print_exc
from typing import Any, cast, ClassVar
from zoneinfo import ZoneInfo

from django.dispatch import Signal
from pokerkit import min_or_none, parse_action

from cardroom.frame import Frame
from cardroom.signals import post_state_construction, pre_state_destruction
from cardroom.table import Table


@dataclass(frozen=True)
class Controller(ABC):
    """The class for real-time table(s) controllers."""

    _lock: ClassVar[RLock] = RLock()
    _controllers: ClassVar[dict[str, Controller]] = {}
    _threads: ClassVar[dict[str, Thread]] = {}

    @classmethod
    def start(cls, name: str, controller: Controller) -> None:
        """Associate a name with a controller and start it.

        :param name: The controller name.
        :param controller: The associated controller.
        :return: ``None``.
        """
        with cls._lock:
            if name in cls._controllers:
                raise ValueError(
                    (
                        f'The name {name} has already been associated with a'
                        ' running controller.'
                    ),
                )

            assert name not in cls._controllers
            assert name not in cls._threads

            thread = Thread(target=controller.mainloop, daemon=True)
            cls._controllers[name] = controller
            cls._threads[name] = thread

            thread.start()

    @classmethod
    def stop(cls, name: str) -> Controller:
        """Stop a controller.

        :param name: The controller name.
        :return: The stopped controller.
        """
        with cls._lock:
            controller = cls._controllers.pop(name)
            thread = cls._threads.pop(name)

        controller.handle('', 'terminate')
        thread.join()

        return controller

    @classmethod
    def lookup(cls, name: str) -> Controller:
        """Lookup a container with the associated name.

        :param name: The controller name.
        :return: The associated controller.
        """
        with cls._lock:
            return cls._controllers[name]

    time_bank: float
    """The time bank."""
    time_bank_increment: float
    """The time bank increment (per hand)."""
    state_construction_timeout: float
    """The state construction timeout."""
    state_destruction_timeout: float
    """The state destruction timeout."""
    idle_timeout: float
    """The idle timeout."""
    standing_pat_timeout: float
    """The standing pat timeout."""
    betting_timeout: float
    """The betting timeout."""
    hole_cards_showing_or_mucking_timeout: float
    """The hole cards showing or mucking timeout."""
    callback: Callable[[list[dict[str, Frame]], tuple[list[str], str]], Any]
    """The callback."""
    parse_value: Callable[[str], int]
    """The value parser."""
    tzinfo: ZoneInfo
    """The timezone."""

    @abstractmethod
    def mainloop(self) -> None:
        """Initiate the mainloop of the cash-game controller.

        :return: ``None``.
        """
        pass

    @abstractmethod
    def handle(self, user: str, event: Any) -> None:
        """Handle the event initiated by a user.

        If the user is system/superuser, the user should be represented
        as an empty string ``''``.

        By design, anonymous users should not be sending events.

        :param user: The user who initiated the event.
        :param event: The initiated event.
        :return: ``None``.
        """
        pass

    def _run(self, table: Table, queue: Queue[tuple[str, Any]]) -> None:

        def get_present_dt() -> datetime:
            return datetime.now(self.tzinfo)

        def is_past(dt: datetime | None) -> bool:
            if dt is None:
                status = False
            else:
                status = get_present_dt() >= dt

            return status

        def get_future_dt(timeout: float) -> datetime:
            return get_present_dt() + timedelta(seconds=timeout)

        def get_auto_dt() -> datetime | None:
            return cast(
                datetime | None,
                min_or_none(
                    (
                        state_construction_dt,
                        state_destruction_dt,
                        *idle_dts.values(),
                        standing_pat_dt,
                        betting_dt,
                        hole_cards_showing_or_mucking_dt,
                    ),
                ),
            )

        def get_event() -> tuple[str, Any] | None:
            if (auto_dt := get_auto_dt()) is not None:
                timeout = max((auto_dt - get_present_dt()).total_seconds(), 0)
            else:
                timeout = None

            try:
                event = queue.get(timeout=timeout)
            except Empty:
                event = None

            return event

        turn_dt: datetime | None = None

        def append_frames() -> None:
            nonlocal turn_dt

            if table.state is None or table.state.turn_index is None:
                turn_dt = None
            elif turn_dt is None:
                turn_dt = get_present_dt()

            auto_dt = min_or_none(
                (
                    standing_pat_dt,
                    betting_dt,
                    hole_cards_showing_or_mucking_dt,
                ),
            )
            timeout: tuple[()] | tuple[datetime] | tuple[datetime, datetime]

            if turn_dt is None:
                timeout = ()
            elif auto_dt is None or auto_dt < turn_dt:
                timeout = (turn_dt,)
            else:
                timeout = turn_dt, auto_dt

            frames.append(Frame.from_table(table, timeout))

        def get_time_bank(user: str) -> float:
            time_banks.setdefault(user, self.time_bank)

            return time_banks[user]

        termination = False

        def parse_user_action() -> None:
            nonlocal termination

            tokens = action.split()

            match tokens:
                case ('terminate',):
                    if user:
                        raise ValueError(
                            f'The user {user} does not have the permission.',
                        )

                    termination = True
                case 'j', seat_index:
                    table.join(user, int(seat_index))
                case ('l',):
                    table.leave(user)
                # TODO
                # case ('s',):
                #     table.sit_out(user)
                case ('b',):
                    table.be_back(user)
                case 'brtr', starting_stack:
                    table.buy_rebuy_top_off_or_rat_hole(
                        user,
                        self.parse_value(starting_stack),
                    )
                case _:
                    seat = table.get_seat(user)

                    if seat is None:
                        raise ValueError(f'The user {user} is not seated.')

                    player_index = seat.player_index

                    if player_index is None:
                        raise ValueError(
                            f'The user {user} is not involved in the hand.',
                        )

                    player = f'p{player_index + 1}'

                    if 'sm' in (tokens := action.split()):
                        if '#' in tokens:
                            tokens = tokens[:tokens.index('#')]

                        if tokens != ['sm'] and tokens != ['sm', '-']:
                            raise ValueError(
                                (
                                    'Explicitly stating showdown is not'
                                    ' permitted for security reasons.'
                                ),
                            )

                    assert table.state is not None

                    parse_action(
                        table.state,
                        f'{player} {action}',
                        self.parse_value,
                    )

        def send_signal(signal: Signal) -> None:
            signal.send(type(self), controller=self, table=table)

        state_construction_dt = None
        state_destruction_dt = None
        idle_dts = dict[str, datetime | None]()
        standing_pat_dt: datetime | None = None
        betting_dt: datetime | None = None
        hole_cards_showing_or_mucking_dt: datetime | None = None

        time_banks = dict[str, float]()
        frames = list[dict[str, Frame]]()
        users_message = list[str](), ''

        append_frames()
        self.callback(frames, users_message)
        frames.clear()

        while not termination:
            user_action = get_event()

            if user_action is not None:
                user, action = user_action

                if isinstance(action, str):
                    try:
                        parse_user_action()
                    except ValueError as exception:
                        if user:
                            users_message = [user], str(exception)
                        else:
                            print_exc()
                    else:
                        append_frames()
                else:
                    if user:
                        users_message = (
                            [user],
                            f'An error occurred when handling {repr(action)}.',
                        )
                    else:
                        print_exc()

            frame_count = None

            while frame_count != len(frames):
                frame_count = len(frames)

                # TODO
                # for user in table.users:
                #     seat = table.get_seat(user)

                #     assert seat is not None

                #     if (
                #             table.state is not None
                #             and not seat.player_status
                #             and not seat.ready_or_postable_status
                #             and not seat.wait_status
                #             and table.can_sit_out(user)
                #     ):
                #         table.sit_out(user)

                #     status = is_past(idle_dts.get(user))

                #     if (
                #             status
                #             or seat.active_status
                #             or not table.can_leave(user)
                #     ):
                #         idle_dts[user] = None
                #     elif idle_dts.get(user) is None:
                #         idle_dts[user] = get_future_dt(
                #             self.idle_timeout,
                #         )

                #     if (
                #             status
                #             and not seat.active_status
                #             and table.can_leave(user)
                #     ):
                #         table.leave(user)
                #         append_frames()

                status = is_past(state_construction_dt)

                if status or not table.can_construct_state():
                    state_construction_dt = None
                elif state_construction_dt is None:
                    state_construction_dt = get_future_dt(
                        self.state_construction_timeout,
                    )

                if status and table.can_construct_state():
                    table.construct_state()
                    send_signal(post_state_construction)
                    append_frames()

                status = is_past(state_destruction_dt)

                if status or not table.can_destroy_state():
                    state_destruction_dt = None
                elif state_destruction_dt is None:
                    state_destruction_dt = get_future_dt(
                        self.state_destruction_timeout,
                    )

                if status and table.can_destroy_state():
                    for user in table.users:
                        time_banks[user] = min(
                            self.time_bank,
                            get_time_bank(user) + self.time_bank_increment,
                        )

                    send_signal(pre_state_destruction)
                    table.destroy_state()
                    append_frames()

                if table.state is None:
                    standing_pat_dt = None
                    betting_dt = None
                    hole_cards_showing_or_mucking_dt = None
                else:
                    if (
                            table.turn_seat is not None
                            and not table.turn_seat.active_status
                    ):
                        if table.state.can_stand_pat_or_discard():
                            table.state.stand_pat_or_discard()
                        elif table.state.can_post_bring_in():
                            table.state.post_bring_in()
                        elif table.state.can_fold():
                            table.state.fold()
                        elif table.state.can_check_or_call():
                            table.state.check_or_call()
                        elif table.state.can_show_or_muck_hole_cards():
                            table.state.show_or_muck_hole_cards()
                        else:
                            raise AssertionError

                        append_frames()

                    status = True

                    if table.state.can_post_ante():
                        table.state.post_ante()
                    elif table.state.can_collect_bets():
                        table.state.collect_bets()
                    elif table.state.can_post_blind_or_straddle():
                        table.state.post_blind_or_straddle()
                    elif table.state.can_deal_board():
                        table.state.deal_board()
                    elif table.state.can_deal_hole():
                        table.state.deal_hole()
                    elif table.state.can_kill_hand():
                        table.state.kill_hand()
                    elif table.state.can_push_chips():
                        table.state.push_chips()
                    elif table.state.can_pull_chips():
                        table.state.pull_chips()
                    else:
                        status = False

                    if status:
                        append_frames()

                    status = is_past(standing_pat_dt)

                    if status or not table.state.can_stand_pat_or_discard():
                        standing_pat_dt = None
                    else:
                        standing_pat_dt = get_future_dt(
                            self.standing_pat_timeout,
                        )

                    if status and table.state.can_stand_pat_or_discard():
                        table.state.stand_pat_or_discard()
                        append_frames()

                    status = is_past(betting_dt)

                    if status or table.state.actor_index is None:
                        betting_dt = None
                    else:
                        betting_dt = get_future_dt(
                            self.betting_timeout,
                        )

                    if status and table.state.actor_index is not None:
                        if table.state.can_fold():
                            table.state.fold()
                        elif table.state.can_check_or_call():
                            table.state.check_or_call()
                        elif table.state.can_post_bring_in():
                            table.state.post_bring_in()
                        else:
                            raise AssertionError

                        append_frames()

                    status = is_past(hole_cards_showing_or_mucking_dt)

                    if status or not table.state.can_show_or_muck_hole_cards():
                        hole_cards_showing_or_mucking_dt = None
                    elif hole_cards_showing_or_mucking_dt is None:
                        hole_cards_showing_or_mucking_dt = (
                            get_future_dt(
                                self.hole_cards_showing_or_mucking_timeout,
                            )
                        )

                    if status and table.state.can_show_or_muck_hole_cards():
                        table.state.show_or_muck_hole_cards()
                        append_frames()

            # TODO
            # for user in set(idle_dts) - set(table.users):
            #     idle_dts.pop(user)

            for user in set(time_banks) - set(table.users):
                time_banks.pop(user)

            self.callback(frames, users_message)
            frames.clear()

            users_message = [], ''


@dataclass(frozen=True)
class CashGame(Controller):
    """The class for cash-game controllers.

    For this type of controller, each controller is associated with just
    a table.
    """

    _table: Table
    _queue: Queue[tuple[str, Any]] = field(
        default_factory=Queue,
        init=False,
    )

    def mainloop(self) -> None:
        self._run(self._table, self._queue)

    def handle(self, user: str, event: Any) -> None:
        self._queue.put((user, event))
