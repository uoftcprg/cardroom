from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Empty, Queue
from typing import Any, cast, Self
from warnings import warn
from zoneinfo import ZoneInfo

from pokerkit import min_or_none, parse_action

from cardroom.table import Table


@dataclass
class Controller(ABC):
    name: str
    """The name."""
    time_bank: float
    """The time bank."""
    time_bank_increment: float
    """The time bank increment."""
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
    callback: Callable[[Self], Any]
    """The callback."""
    parse_value: Callable[[str], int]
    """The value parser."""
    tzinfo: ZoneInfo
    """The timezone."""
    time_banks: dict[str, float] = field(default_factory=dict, init=False)
    """The time banks."""
    timestamp: datetime = field(init=False)
    """The timestamp."""
    auto_timestamp: datetime | None = field(default=None, init=False)
    """The auto timestamp."""

    def __post_init__(self) -> None:
        self.timestamp = datetime.now(self.tzinfo)

    @abstractmethod
    def mainloop(self) -> None:
        pass

    @abstractmethod
    def handle(self, user: str, event: Any) -> None:
        pass

    def _run(self, table: Table, queue: Queue[tuple[str, Any]]) -> None:

        def is_past_timestamp(timestamp: datetime | None) -> bool:
            if timestamp is None:
                status = False
            else:
                status = get_now_timestamp() >= timestamp

            return status

        def get_now_timestamp() -> datetime:
            return datetime.now(self.tzinfo)

        def get_future_timestamp(timeout: float | None) -> datetime | None:
            if timeout is None:
                timestamp = None
            else:
                timestamp = get_now_timestamp() + timedelta(seconds=timeout)

            return timestamp

        def get_auto_timestamp() -> datetime | None:
            return cast(
                datetime | None,
                min_or_none(
                    (
                        state_construction_timestamp,
                        state_destruction_timestamp,
                        *idle_timestamps.values(),
                        standing_pat_timestamp,
                        betting_timestamp,
                        hole_cards_showing_or_mucking_timeout,
                    ),
                ),
            )

        def get_event() -> tuple[str, Any] | None:
            if (auto_timestamp := get_auto_timestamp()) is not None:
                timeout = max(
                    (auto_timestamp - get_now_timestamp()).seconds,
                    0,
                )
            else:
                timeout = None

            try:
                event = queue.get(timeout=timeout)
            except Empty:
                event = None

            return event

        state_construction_timestamp = None
        state_destruction_timestamp = None
        idle_timestamps = dict[str, datetime | None]()
        standing_pat_timestamp = None
        betting_timestamp = None
        hole_cards_showing_or_mucking_timestamp = None

        while user_action := get_event():
            if user_action is not None:
                user, action = user_action

                if isinstance(action, str):
                    self._parse_user_action(table, user, action)
                else:
                    warn('cannot handle event')

            status = True

            while status:
                status = False
                state_construction_timeout = None

                if table.can_construct_state():
                    if is_past_timestamp(state_construction_timestamp):
                        table.construct_state()

                        status = True
                    else:
                        state_construction_timeout = (
                            self.state_construction_timeout
                        )

                state_construction_timestamp = min_or_none(
                    (
                        state_construction_timestamp,
                        get_future_timestamp(state_construction_timeout),
                    ),
                )
                state_destruction_timeout = None

                if table.can_destroy_state():
                    if is_past_timestamp(state_destruction_timestamp):
                        table.destroy_state()

                        # TODO: increase time banks

                        status = True
                    else:
                        state_destruction_timeout = (
                            self.state_destruction_timeout
                        )

                state_destruction_timestamp = min_or_none(
                    (
                        state_destruction_timestamp,
                        get_future_timestamp(state_destruction_timeout),
                    ),
                )

                for user in table.users:
                    seat = table.get_seat(user)

                    if (
                            table.state is not None
                            and not seat.player_status
                            and table.can_sit_out(user)
                    ):
                        table.sit_out(user)

                        status = True

                    idle_timeout = None

                    if (
                        not seat.active_status
                        and table.can_leave(user)
                    ):
                        if is_past_timestamp(idle_timestamps.get(user)):
                            table.leave(user)

                            status = True
                        else:
                            idle_timeout = self.idle_timeout

                    idle_timestamps[user] = get_future_timestamp(idle_timeout)

                if table.state is not None:
                    if table.state.can_post_ante():
                        table.state.post_ante()

                        status = True

                    if table.state.can_collect_bets():
                        table.state.collect_bets()

                        status = True

                    if table.state.can_post_blind_or_straddle():
                        table.state.post_blind_or_straddle()

                        status = True

                    if table.state.can_burn_card():
                        table.state.burn_card()

                        status = True

                    if table.state.can_deal_board():
                        table.state.deal_board()

                        status = True

                    if table.state.can_deal_hole():
                        table.state.deal_hole()

                        status = True

                    standing_pat_timeout = None

                    if table.state.can_stand_pat_or_discard():
                        if is_past_timestamp(standing_pat_timestamp):
                            table.state.stand_pat_or_discard()

                            status = True
                        else:
                            standing_pat_timeout = self.standing_pat_timeout

                    standing_pat_timestamp = min_or_none(
                        (
                            standing_pat_timestamp,
                            get_future_timestamp(standing_pat_timeout),
                        ),
                    )
                    betting_timeout = None

                    if table.state.actor_index is not None:
                        # TODO: use time banks

                        if is_past_timestamp(betting_timestamp):
                            if table.state.can_fold():
                                table.state.fold()

                                status = True
                            elif table.state.can_check_or_call():
                                table.state.check_or_call()

                                status = True
                            elif table.state.can_post_bring_in():
                                table.state.post_bring_in()

                                status = True
                            else:
                                raise AssertionError
                        else:
                            betting_timeout = self.betting_timeout

                    betting_timestamp = min_or_none(
                        (
                            betting_timestamp,
                            get_future_timestamp(betting_timeout),
                        ),
                    )
                    hole_cards_showing_or_mucking_timeout = None

                    if table.state.can_show_or_muck_hole_cards():
                        if (
                                is_past_timestamp(
                                    hole_cards_showing_or_mucking_timestamp,
                                )
                        ):
                            table.state.show_or_muck_hole_cards()

                            status = True
                        else:
                            hole_cards_showing_or_mucking_timeout = (
                                self.hole_cards_showing_or_mucking_timeout
                            )

                    hole_cards_showing_or_mucking_timestamp = min_or_none(
                        (
                            hole_cards_showing_or_mucking_timestamp,
                            get_future_timestamp(
                                hole_cards_showing_or_mucking_timeout,
                            ),
                        ),
                    )

                    if table.state.can_kill_hand():
                        table.state.kill_hand()

                        status = True

                    if table.state.can_push_chips():
                        table.state.push_chips()

                        status = True

                    if table.state.can_pull_chips():
                        table.state.pull_chips()

                        status = True

            for user in set(idle_timestamps) - set(table.users):
                idle_timestamps.pop(user)

            for user in set(self.time_banks) - set(table.users):
                self.time_banks.pop(user)

            self.timestamp = get_now_timestamp()
            self.auto_timestamp = get_auto_timestamp()

            self.callback(self)

    def _parse_user_action(self, table: Table, user: str, action: str) -> None:
        tokens = action.split()

        if table.can_be_back(user):
            table.be_back(user)

        match tokens:
            case 's', seat_index:
                table.sit(user, int(seat_index))
            case ('l',):
                table.leave(user)
            case ('so',):
                table.sit_out(user)
            case ('bb',):
                table.be_back(user)
            case 'rtr', starting_stack:
                table.rebuy_top_off_or_rat_hole(
                    user,
                    self.parse_value(starting_stack),
                )
            case _:
                player_index = table.get_seat(user).player_index

                if player_index is None:
                    raise ValueError('player dne')

                player = f'p{player_index + 1}'

                if table.state is None:
                    raise ValueError('state dne')

                parse_action(
                    table.state,
                    f'{player} {action}',
                    self.parse_value,
                )


@dataclass
class CashGame(Controller):
    table: Table
    """The table."""
    queue: Queue[tuple[str, Any]] = field(default_factory=Queue, init=False)
    """The queue."""

    def mainloop(self) -> None:
        self._run(self.table, self.queue)

    def handle(self, user: str, event: Any) -> None:
        self.queue.put((user, event))


@dataclass
class Tournament(Controller):
    def mainloop(self) -> None:
        raise NotImplementedError

    def handle(self, user: str, event: Any) -> None:
        raise NotImplementedError
