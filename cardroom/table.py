from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Condition, RLock, Timer
from typing import Any, ClassVar

from pokerkit import CardsLike, State
from pokerkit.state import Operation  # TODO


@dataclass
class Table:
    CONDITION_WAIT_TIMEOUT: ClassVar[float] = 1

    seat_count: int
    idle_timeout: float
    ante_posting_timeout: float
    bet_collection_timeout: float
    blind_or_straddle_posting_timeout: float
    card_burning_timeout: float
    hole_dealing_timeout: float
    board_dealing_timeout: float
    standing_pat_timeout: float
    folding_timeout: float
    checking_timeout: float
    bring_in_posting_timeout: float
    hole_cards_showing_or_mucking_timeout: float
    hand_killing_timeout: float
    chips_pushing_timeout: float
    chips_pulling_timeout: float
    skip_timeout: float
    callback: Callable[[Table, Operation | None], Any]

    player_names: list[str | None] = field(init=False, default_factory=list)
    player_indices: list[int | None] = field(init=False, default_factory=list)
    final_stack: list[int | None] = field(init=False, default_factory=list)
    buy_in_top_off_or_rat_holing_amounts: list[int | None] = field(
        init=False,
        default_factory=list,
    )
    inactive_timestamps: list[datetime | None] = field(
        init=False,
        default_factory=list,
    )
    connection_statuses: list[bool] = field(init=False, default_factory=list)

    state: State | None = field(init=False, default=None)

    _state_update_count: int = field(init=False, default=0)
    _update_status: bool = field(init=False, default=False)
    _termination_status: bool = field(init=False, default=False)
    _lock: RLock = field(init=False, default_factory=RLock)
    _condition: Condition = field(init=False)

    def __post_init__(self) -> None:
        self._condition = Condition(self._lock)

        for _ in range(self.seat_count):
            self.player_names.append(None)
            self.player_indices.append(None)
            self.buy_in_top_off_or_rat_holing_amounts.append(None)
            self.inactive_timestamps.append(None)
            self.connection_statuses.append(False)

    @property
    def seat_indices(self) -> range:
        return range(self.seat_count)

    @property
    def activity_statuses(self) -> list[bool]:
        with self._lock:
            return [
                timestamp is None for timestamp in self.inactive_timestamps
            ]

    def get_seat_index(self, player_name_or_player_index: str | int) -> int:
        with self._lock:
            for i, (player_name, player_index) in enumerate(
                    zip(self.player_names, self.player_indices),
            ):
                if (
                        player_name == player_name_or_player_index
                        or player_index == player_name_or_player_index
                ):
                    return i

        raise ValueError('unknown player name or player index')

    def get_player_index(
            self,
            seat_index_or_player_name: int | str,
    ) -> int | None:
        with self._lock:
            for i, (seat_index, player_name) in enumerate(
                    zip(self.seat_indices, self.player_names),
            ):
                if (
                        seat_index == seat_index_or_player_name
                        or player_name == seat_index_or_player_name
                ):
                    return self.player_indices[i]

        raise ValueError('unknown seat index or player name')

    def mainloop(self) -> None:
        with self._condition:
            while not self._termination_status:
                self._condition.wait_for(
                    lambda: self._update_status,
                    self.CONDITION_WAIT_TIMEOUT,
                )
                self._update_status = False

                if self.state is None:
                    pass  # TODO
                else:
                    if self.state.can_post_ante():
                        self._update_state(
                            self.ante_posting_timeout,
                            self.state.post_ante,
                        )
                    elif self.state.can_collect_bets():
                        self._update_state(
                            self.bet_collection_timeout,
                            self.state.collect_bets,
                        )
                    elif self.state.can_post_blind_or_straddle():
                        self._update_state(
                            self.blind_or_straddle_posting_timeout,
                            self.state.post_blind_or_straddle,
                        )
                    elif self.state.can_burn_card():
                        self._update_state(
                            self.card_burning_timeout,
                            self.state.burn_card,
                        )
                    elif self.state.can_deal_hole():
                        self._update_state(
                            self.hole_dealing_timeout,
                            self.state.deal_hole,
                        )
                    elif self.state.can_deal_board():
                        self._update_state(
                            self.board_dealing_timeout,
                            self.state.deal_board,
                        )
                    elif self.state.can_stand_pat_or_discard():
                        assert (
                            self.state.stander_pat_or_discarder_index
                            is not None
                        )

                        seat_index = self.get_seat_index(
                            self.state.stander_pat_or_discarder_index,
                        )

                        if self.activity_statuses[seat_index]:
                            timeout = self.standing_pat_timeout
                        else:
                            timeout = self.skip_timeout

                        self._update_state(
                            timeout,
                            self._deactivate_and,
                            seat_index,
                            self.state.stand_pat_or_discard,
                        )
                    elif self.state.can_fold():
                        assert self.state.actor_index is not None

                        seat_index = self.get_seat_index(
                            self.state.actor_index,
                        )

                        if self.activity_statuses[seat_index]:
                            timeout = self.folding_timeout
                        else:
                            timeout = self.skip_timeout

                        self._update_state(
                            timeout,
                            self._deactivate_and,
                            seat_index,
                            self.state.fold,
                        )
                    elif self.state.can_check_or_call():
                        assert self.state.actor_index is not None

                        seat_index = self.get_seat_index(
                            self.state.actor_index,
                        )

                        if self.activity_statuses[seat_index]:
                            timeout = self.checking_timeout
                        else:
                            timeout = self.skip_timeout

                        self._update_state(
                            timeout,
                            self._deactivate_and,
                            seat_index,
                            self.state.check_or_call,
                        )
                    elif self.state.can_post_bring_in():
                        assert self.state.actor_index is not None

                        seat_index = self.get_seat_index(
                            self.state.actor_index,
                        )

                        if self.activity_statuses[seat_index]:
                            timeout = self.bring_in_posting_timeout
                        else:
                            timeout = self.skip_timeout

                        self._update_state(
                            timeout,
                            self._deactivate_and,
                            seat_index,
                            self.state.post_bring_in,
                        )
                    elif self.state.can_show_or_muck_hole_cards():
                        assert self.state.showdown_index is not None

                        seat_index = self.get_seat_index(
                            self.state.showdown_index,
                        )

                        if self.activity_statuses[seat_index]:
                            timeout = (
                                self.hole_cards_showing_or_mucking_timeout
                            )
                        else:
                            timeout = self.skip_timeout

                        self._update_state(
                            timeout,
                            self.state.show_or_muck_hole_cards,
                        )
                    elif self.state.can_kill_hand():
                        self._update_state(
                            self.hand_killing_timeout,
                            self.state.kill_hand,
                        )
                    elif self.state.can_push_chips():
                        self._update_state(
                            self.chips_pushing_timeout,
                            self.state.push_chips,
                        )
                    elif self.state.can_pull_chips():
                        self._update_state(
                            self.chips_pulling_timeout,
                            self.state.pull_chips,
                        )

    def connect(self, player_name: str, seat_index: int, amount: int) -> None:
        with self._lock:
            self._update(0, self._connect, seat_index, player_name, amount)

    def disconnect(self, player_name: str) -> None:
        with self._lock:
            self._update(0, self._disconnect, self.get_seat_index(player_name))

    def activate(self, player_name: str) -> None:
        with self._lock:
            self._update(0, self._activate, self.get_seat_index(player_name))

    def deactivate(self, player_name: str) -> None:
        with self._lock:
            self._update(0, self._deactivate, self.get_seat_index(player_name))

    def buy_in_top_off_or_rat_hole(
            self,
            player_name: str,
            amount: int,
    ) -> None:
        with self._lock:
            self._update_state(
                0,
                self._activate_and,
                self.get_seat_index(player_name),
                self._buy_in_top_off_or_rat_hole,
                self.get_seat_index(player_name),
                amount,
            )

    def stand_pat_or_discard(
            self,
            player_name: str,
            cards: CardsLike = None,
    ) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.stander_pat_or_discarder_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.stander_pat_or_discarder_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(
                        self.state.stander_pat_or_discarder_index,
                    ),
                    self.state.stand_pat_or_discard,
                    cards,
                )

    def fold(self, player_name: str) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.actor_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.actor_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(self.state.actor_index),
                    self.state.fold,
                )

    def check_or_call(self, player_name: str) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.actor_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.actor_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(self.state.actor_index),
                    self.state.check_or_call,
                )

    def post_bring_in(self, player_name: str) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.actor_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.actor_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(self.state.actor_index),
                    self.state.post_bring_in,
                )

    def complete_bet_or_raise_to(
            self,
            player_name: str,
            amount: int | None = None,
    ) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.actor_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.actor_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(self.state.actor_index),
                    self.state.complete_bet_or_raise_to,
                    amount,
                )

    def show_or_muck_hole_cards(
            self,
            player_name: str,
            status: bool | None = None,
    ) -> None:
        with self._lock:
            if (
                    self.state is not None
                    and (
                        self.state.showdown_index
                        == self.get_player_index(player_name)
                    )
            ):
                assert self.state.showdown_index is not None

                self._update_state(
                    0,
                    self._activate_and,
                    self.get_seat_index(self.state.showdown_index),
                    self.state.show_or_muck_hole_cards,
                    status,
                )

    def _connect(
            self,
            seat_index: int,
            player_name: str,
            amount: int,
    ) -> None:
        with self._lock:
            self.player_names[seat_index] = player_name
            self.player_indices[seat_index] = None
            self.buy_in_top_off_or_rat_holing_amounts[seat_index] = amount
            self.inactive_timestamps[seat_index] = None
            self.connection_statuses[seat_index] = True

            self._activate(seat_index)

    def _disconnect(
            self,
            seat_index: int,
    ) -> None:
        with self._lock:
            self.connection_statuses[seat_index] = False

            self._deactivate(seat_index)

    def _activate(self, seat_index: int) -> None:
        with self._lock:
            assert self.player_names[seat_index] is not None

            self.inactive_timestamps[seat_index] = None

    def _activate_and(
            self,
            seat_index: int,
            method: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> Operation | None:
        with self._lock:
            self._activate(seat_index)

            return method(*args, **kwargs)

    def _deactivate(self, seat_index: int) -> None:
        with self._lock:
            assert self.player_names[seat_index] is not None

            if self.inactive_timestamps[seat_index] is None:
                self.inactive_timestamps[seat_index] = datetime.now()

    def _deactivate_and(
            self,
            seat_index: int,
            method: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> Operation | None:
        with self._lock:
            self._deactivate(seat_index)

            return method(*args, **kwargs)

    def _buy_in_top_off_or_rat_hole(
            self,
            seat_index: int,
            amount: int,
    ) -> None:
        with self._lock:
            self.buy_in_top_off_or_rat_holing_amounts[seat_index] = amount

    def _update(
            self,
            timeout: float,
            method: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> None:

        def function() -> None:
            with self._condition:
                operation = method(*args, **kwargs)

                self.callback(self, operation)
                self._update_status = True
                self._condition.notify()

        Timer(timeout, function).start()

    def _update_state(
            self,
            timeout: float,
            method: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> None:

        def function() -> Operation | None:
            with self._lock:
                if state_update_count != self._state_update_count:
                    raise ValueError('obsolete update')

                self._state_update_count += 1

                return method(*args, **kwargs)

        state_update_count = self._state_update_count

        self._update(timeout, function)
