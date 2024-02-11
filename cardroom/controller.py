from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Empty, Queue
from traceback import print_exc
from typing import Any
from warnings import warn
from zoneinfo import ZoneInfo

from pokerkit import min_or_none, parse_action

from cardroom.felt import Frame
from cardroom.table import Table


@dataclass
class Controller(ABC):
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
    callback: Callable[[list[dict[str, Frame]], tuple[list[str], str]], Any]
    """The callback."""
    parse_value: Callable[[str], int]
    """The value parser."""
    tzinfo: ZoneInfo
    """The timezone."""

    @abstractmethod
    def mainloop(self) -> None:
        pass

    @abstractmethod
    def handle(self, user: str, event: Any) -> None:
        pass

    def _run(self, table: Table, queue: Queue[tuple[str, Any]]) -> None:

        def get_now_timestamp() -> datetime:
            return datetime.now(self.tzinfo)

        def is_past_timestamp(timestamp: datetime | None) -> bool:
            if timestamp is None:
                status = False
            else:
                status = get_now_timestamp() >= timestamp

            return status

        def get_future_timestamp(timeout: float) -> datetime:
            return get_now_timestamp() + timedelta(seconds=timeout)

        def get_auto_timestamp() -> datetime | None:
            return min_or_none(
                (
                    state_construction_timestamp,
                    state_destruction_timestamp,
                    *idle_timestamps.values(),
                    standing_pat_timestamp,
                    betting_timestamp,
                    hole_cards_showing_or_mucking_timestamp,
                ),
            )

        def get_event() -> tuple[str, Any] | None:
            if (auto_timestamp := get_auto_timestamp()) is not None:
                timeout = max(
                    (auto_timestamp - get_now_timestamp()).total_seconds(),
                    0,
                )
            else:
                timeout = None

            try:
                event = queue.get(timeout=timeout)
            except Empty:
                event = None

            return event

        def append_frames() -> None:
            frames.append(Frame.from_table(table))

        def get_time_bank(user: str) -> float:
            time_banks.setdefault(user, self.time_bank)

            return time_banks[user]

        state_construction_timestamp = None
        state_destruction_timestamp = None
        idle_timestamps = dict[str, datetime | None]()
        standing_pat_timestamp: datetime | None = None
        betting_timestamp: datetime | None = None
        hole_cards_showing_or_mucking_timestamp: datetime | None = None

        def parse_user_action() -> None:
            nonlocal standing_pat_timestamp
            nonlocal betting_timestamp
            nonlocal hole_cards_showing_or_mucking_timestamp

            tokens = action.split()

            match tokens:
                case 'j', seat_index:
                    table.join(user, int(seat_index))
                case ('l',):
                    table.leave(user)
                case ('s',):
                    table.sit_out(user)
                case ('b',):
                    table.be_back(user)
                case 'brtr', starting_stack:
                    table.buy_rebuy_top_off_or_rat_hole(
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

                    if 'sm' in (tokens := action.split()):
                        if '#' in tokens:
                            tokens = tokens[:tokens.index('#')]

                        if tokens != ['sm'] or tokens != ['sm', '-']:
                            raise ValueError('explicit showdown is forbidden')

                    parse_action(
                        table.state,
                        f'{player} {action}',
                        self.parse_value,
                    )

                    standing_pat_timestamp = None
                    betting_timestamp = None
                    hole_cards_showing_or_mucking_timestamp = None

        time_banks = dict[str, float]()
        frames = list[dict[str, Frame]]()
        users_message = list[str](), ''

        append_frames()
        self.callback(frames, users_message)
        frames.clear()

        while True:
            user_action = get_event()

            if user_action is not None:
                user, action = user_action

                if isinstance(action, str):
                    try:
                        parse_user_action()
                    except ValueError as exception:
                        users_message = [user], str(exception)

                        print_exc()
                    else:
                        append_frames()
                else:
                    warn('cannot handle event')

            frame_count = None

            while frame_count != len(frames):
                frame_count = len(frames)

                for user in table.users:
                    seat = table.get_seat(user)

                    if (
                            table.state is not None
                            and not seat.player_status
                            and table.can_sit_out(user)
                    ):
                        table.sit_out(user)

                    status = is_past_timestamp(idle_timestamps.get(user))

                    if (
                            status
                            or seat.active_status
                            or not table.can_leave(user)
                    ):
                        idle_timestamps[user] = None
                    elif idle_timestamps.get(user) is None:
                        idle_timestamps[user] = get_future_timestamp(
                            self.idle_timeout,
                        )

                    if (
                            status
                            and not seat.active_status
                            and table.can_leave(user)
                    ):
                        table.leave(user)
                        append_frames()

                status = is_past_timestamp(state_construction_timestamp)

                if status or not table.can_construct_state():
                    state_construction_timestamp = None
                elif state_construction_timestamp is None:
                    state_construction_timestamp = get_future_timestamp(
                        self.state_construction_timeout,
                    )

                if status and table.can_construct_state():
                    table.construct_state()
                    append_frames()

                status = is_past_timestamp(state_destruction_timestamp)

                if status or not table.can_destroy_state():
                    state_destruction_timestamp = None
                elif state_destruction_timestamp is None:
                    state_destruction_timestamp = get_future_timestamp(
                        self.state_destruction_timeout,
                    )

                if status and table.can_destroy_state():
                    for key, value in time_banks.items():
                        time_banks[key] = min(
                            self.time_bank,
                            value + self.time_bank_increment,
                        )

                    table.destroy_state()
                    append_frames()

                if table.state is None:
                    standing_pat_timestamp = None
                    betting_timestamp = None
                    hole_cards_showing_or_mucking_timestamp = None
                else:
                    if (
                            table.acting_seat is not None
                            and not table.acting_seat.active_status
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

                    status = is_past_timestamp(standing_pat_timestamp)

                    if status or not table.state.can_stand_pat_or_discard():
                        standing_pat_timestamp = None
                    else:
                        standing_pat_timestamp = get_future_timestamp(
                            self.standing_pat_timeout,
                        )

                    if status and table.state.can_stand_pat_or_discard():
                        table.state.stand_pat_or_discard()
                        append_frames()

                    status = is_past_timestamp(betting_timestamp)

                    if status or table.state.actor_index is None:
                        betting_timestamp = None
                    else:
                        betting_timestamp = get_future_timestamp(
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

                    status = is_past_timestamp(
                        hole_cards_showing_or_mucking_timestamp,
                    )

                    if status or not table.state.can_show_or_muck_hole_cards():
                        hole_cards_showing_or_mucking_timestamp = None
                    elif hole_cards_showing_or_mucking_timestamp is None:
                        hole_cards_showing_or_mucking_timestamp = (
                            get_future_timestamp(
                                self.hole_cards_showing_or_mucking_timeout,
                            )
                        )

                    if status and table.state.can_show_or_muck_hole_cards():
                        table.state.show_or_muck_hole_cards()
                        append_frames()

            for user in set(idle_timestamps) - set(table.users):
                idle_timestamps.pop(user)

            for user in set(time_banks) - set(table.users):
                time_banks.pop(user)

            # TODO: send over
            # timestamp = get_now_timestamp()
            # auto_timestamp = get_auto_timestamp()

            if frames or users_message is not None:
                self.callback(frames, users_message)

            frames.clear()
            users_message = [], ''


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
