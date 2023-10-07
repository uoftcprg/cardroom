""":mod:`cardroom.table` implements classes related to cardroom tables."""

from __future__ import annotations

from collections.abc import Callable
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from traceback import format_exc
from typing import Any
from warnings import warn

from pokerkit import (
    BettingStructure,
    CardsLike,
    Deck,
    Hand,
    Operation,
    State,
    Street,
    ValuesLike,
)

from cardroom.utilities import Scheduler


@dataclass
class Table:
    """The class for cardroom tables."""

    seat_count: int
    """The number of seats."""
    button_status: bool
    """The button status."""
    deck: Deck
    """The deck."""
    hand_types: tuple[type[Hand], ...]
    """The hand types."""
    streets: tuple[Street, ...]
    """The streets."""
    betting_structure: BettingStructure
    """The betting structure."""
    ante_trimming_status: bool
    """The ante trimming status.

    Usually, if you want uniform antes, set this to ``True``. If you
    want non-uniform antes like big blind antes, set this to ``False``.
    """
    raw_antes: ValuesLike
    """The raw antes."""
    raw_blinds_or_straddles: ValuesLike
    """The raw blinds or straddles."""
    bring_in: int
    """The bring-in."""
    buy_in_range: range
    """The buy-in range."""
    timebank: float
    """The timebank."""
    timebank_increment: float
    """The timebank increment."""
    play_timeout: float
    """The play timeout."""
    idle_timeout: float
    """The idle timeout."""
    ante_posting_timeout: float
    """The ante posting timeout."""
    bet_collection_timeout: float
    """The bet collection timeout."""
    blind_or_straddle_posting_timeout: float
    """The blind or straddle posting timeout."""
    card_burning_timeout: float
    """The card burning timeout."""
    hole_dealing_timeout: float
    """The hole dealing timeout."""
    board_dealing_timeout: float
    """The board dealing timeout."""
    standing_pat_timeout: float
    """The standing pat timeout."""
    folding_timeout: float
    """The folding timeout."""
    checking_timeout: float
    """The checking timeout."""
    bring_in_posting_timeout: float
    """The bring-in posting timeout."""
    hole_cards_showing_or_mucking_timeout: float
    """The hole cards showing or mucking timeout."""
    hand_killing_timeout: float
    """The hand killing timeout."""
    chips_pushing_timeout: float
    """The chips pushing timeout."""
    chips_pulling_timeout: float
    """The chips pulling timeout."""
    skip_timeout: float
    """The skip timeout."""
    callback: Callable[[Table, Operation | None], Any]
    """The callback."""
    player_names: list[str | None] = field(init=False, default_factory=list)
    """The player names."""
    player_indices: list[int | None] = field(init=False, default_factory=list)
    """The player indices."""
    starting_stacks: list[int | None] = field(init=False, default_factory=list)
    """The starting stacks."""
    buy_in_rebuy_top_off_or_rat_holing_amounts: list[int | None] = field(
        init=False,
        default_factory=list,
    )
    """The buy-in, rebuy, top-off, or rat-holing amounts."""
    active_timestamps: list[datetime | None] = field(
        init=False,
        default_factory=list,
    )
    """The active timestamps."""
    inactive_timestamps: list[datetime | None] = field(
        init=False,
        default_factory=list,
    )
    """The inactive timestamps."""
    timebanks: list[float | None] = field(init=False, default_factory=list)
    """The timebanks."""
    state: State | None = field(init=False, default=None)
    """The state."""
    button_index: int | None = field(init=False, default=None)
    """The button index."""

    def __post_init__(self) -> None:
        for _ in range(self.seat_count):
            self.player_names.append(None)
            self.player_indices.append(None)
            self.starting_stacks.append(None)
            self.buy_in_rebuy_top_off_or_rat_holing_amounts.append(None)
            self.active_timestamps.append(None)
            self.inactive_timestamps.append(None)
            self.timebanks.append(None)

    @property
    def seat_indices(self) -> range:
        """Return the seat indices.

        :return: The seat indices.
        """
        return range(self.seat_count)

    @property
    def turn_index(self) -> int | None:
        """Return the turn index, if any.

        The turn index corresponds to the player index, not the seat
        index.

        :return: The optional turn index.
        """
        turn_index = None

        if self.state is not None:
            if self.state.stander_pat_or_discarder_index is not None:
                turn_index = self.state.stander_pat_or_discarder_index
            elif self.state.actor_index is not None:
                turn_index = self.state.actor_index
            elif self.state.showdown_index is not None:
                turn_index = self.state.showdown_index

        return turn_index

    def is_occupied(self, seat_index: int) -> bool:
        """Return the occupation status of the seat.

        :param seat_index: The seat index.
        :return: The occupation status of the seat.
        """
        return self.player_names[seat_index] is not None

    def is_active(self, seat_index: int) -> bool:
        """Return the active status of the player at the seat.

        :param seat_index: The seat index.
        :return: The active status of the player at the seat.
        """
        return (
            self.is_occupied(seat_index)
            and self.inactive_timestamps[seat_index] is None
        )

    def is_kickable(self, seat_index: int) -> bool:
        """Return the kickable status of the player at the seat.

        :param seat_index: The seat index.
        :return: The kickable status of the player at the seat.
        """
        inactive_timestamp = self.inactive_timestamps[seat_index]

        return (
            self.is_occupied(seat_index)
            and inactive_timestamp is not None
            and (
                inactive_timestamp
                + timedelta(seconds=self.idle_timeout)
                <= datetime.now()
            )
        )

    def get_seat_index(self, player_name_or_player_index: str | int) -> int:
        """Return the seat index of the player.

        :param player_name_or_player_index: The player name or the
                                            player index.
        :return: The seat index of the player.
        """
        if (
                isinstance(player_name_or_player_index, str)
                and player_name_or_player_index in self.player_names
        ):
            return self.player_names.index(player_name_or_player_index)
        elif (
                isinstance(player_name_or_player_index, int)
                and player_name_or_player_index in self.player_indices
        ):
            return self.player_indices.index(player_name_or_player_index)

        raise ValueError('unknown player name or player index')

    def connect(self, player_name: str, seat_index: int, amount: int) -> None:
        """Connect the player.

        :param player_name: The player name.
        :param seat_index: The seat index.
        :param amount: The buy-in amount.
        :return: ``None``.
        """
        self._call(0, self._connect, player_name, seat_index, amount)

    def _connect(self, player_name: str, seat_index: int, amount: int) -> None:
        if seat_index not in self.seat_indices:
            raise ValueError('seat index out of bounds')
        elif amount < 0:
            raise ValueError('negative amount')
        elif amount not in self.buy_in_range:
            raise ValueError('invalid buy-in amount')
        elif self.is_occupied(seat_index):
            raise ValueError('occupied seat')

        self.player_names[seat_index] = player_name
        self.player_indices[seat_index] = None
        self.starting_stacks[seat_index] = None
        self.buy_in_rebuy_top_off_or_rat_holing_amounts[seat_index] = amount
        self.active_timestamps[seat_index] = None
        self.inactive_timestamps[seat_index] = None
        self.timebanks[seat_index] = self.timebank

    def disconnect(self, player_name: str) -> None:
        """Disconnect the player.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call(0, self._disconnect, player_name)

    def _disconnect(self, player_name: str) -> None:
        seat_index = self.get_seat_index(player_name)
        self.inactive_timestamps[seat_index] = datetime.min

    def activate(self, player_name: str) -> None:
        """Activate the player.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call(0, self._activate, player_name)

    def _activate(self, player_name: str) -> None:
        seat_index = self.get_seat_index(player_name)
        self.inactive_timestamps[seat_index] = None

    def deactivate(self, player_name: str) -> None:
        """Deactivate the player.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call(0, self._deactivate, player_name)

    def _deactivate(self, player_name: str) -> None:
        seat_index = self.get_seat_index(player_name)

        if self.inactive_timestamps[seat_index] is None:
            self.inactive_timestamps[seat_index] = datetime.now()

    def buy_in_rebuy_top_off_or_rat_hole(
            self,
            player_name: str,
            amount: int,
    ) -> None:
        """Buy in, rebuy, top-off, or rat-hole.

        :param player_name: The player name.
        :param amount: The amount.
        :return: ``None``.
        """
        self._call(
            0,
            self._buy_in_rebuy_top_off_or_rat_hole,
            player_name,
            amount,
        )

    def _buy_in_rebuy_top_off_or_rat_hole(
            self,
            player_name: str,
            amount: int,
    ) -> None:
        if amount < 0:
            raise ValueError('negative amount')
        elif amount not in self.buy_in_range:
            raise ValueError('invalid buy-in amount')

        self._activate(player_name)

        seat_index = self.get_seat_index(player_name)
        self.buy_in_rebuy_top_off_or_rat_holing_amounts[seat_index] = amount

    def stand_pat_or_discard(
            self,
            player_name: str,
            cards: CardsLike = None,
    ) -> None:
        """Stand pat or discard.

        :param player_name: The player name.
        :param cards: The cards.
        :return: ``None``.
        """
        self._call_state(player_name, 0, State.stand_pat_or_discard, cards)

    def fold(self, player_name: str) -> None:
        """Fold.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call_state(player_name, 0, State.fold)

    def check_or_call(self, player_name: str) -> None:
        """Check or call.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call_state(player_name, 0, State.check_or_call)

    def post_bring_in(self, player_name: str) -> None:
        """Post bring-in.

        :param player_name: The player name.
        :return: ``None``.
        """
        self._call_state(player_name, 0, State.post_bring_in)

    def complete_bet_or_raise_to(
            self,
            player_name: str,
            amount: int | None = None,
    ) -> None:
        """Complete, bet, or raise to.

        :param player_name: The player name.
        :param amount: The optional amount.
        :return: ``None``.
        """
        self._call_state(
            player_name,
            0,
            State.complete_bet_or_raise_to,
            amount,
        )

    def show_or_muck_hole_cards(
            self,
            player_name: str,
            status: bool | None = None,
    ) -> None:
        """Show or muck hole cards.

        :param player_name: The player name.
        :param status: The optional status.
        :return: ``None``.
        """
        self._call_state(
            player_name,
            0,
            State.show_or_muck_hole_cards,
            status,
        )

    def _play(self) -> None:
        if self.state is not None:
            if self.state.status:
                raise ValueError('state active')

            for i in self.seat_indices:
                player_index = self.player_indices[i]

                if player_index is None:
                    self.starting_stacks[i] = None
                else:
                    self.starting_stacks[i] = self.state.stacks[player_index]

                self.player_indices[i] = None
                timebank = self.timebanks[i]

                if timebank is not None:
                    self.timebanks[i] = min(
                        self.timebank,
                        timebank + self.timebank_increment,
                    )

            self.state = None

        for i in self.seat_indices:
            if (
                    self.buy_in_rebuy_top_off_or_rat_holing_amounts[i]
                    is not None
            ):
                self.starting_stacks[i] = (
                    self.buy_in_rebuy_top_off_or_rat_holing_amounts[i]
                )

            self.buy_in_rebuy_top_off_or_rat_holing_amounts[i] = None

            if self.starting_stacks[i] == 0:
                player_name = self.player_names[i]

                assert player_name is not None

                self._deactivate(player_name)

                self.starting_stacks[i] = None

        active_seat_indices = deque(filter(self.is_active, self.seat_indices))

        if len(active_seat_indices) >= 2:
            if self.button_status:
                if (
                        self.button_index is None
                        or self.button_index >= active_seat_indices[-1]
                ):
                    self.button_index = active_seat_indices[0]
                else:
                    self.button_index = next(
                        i for i in active_seat_indices if i > self.button_index
                    )

                active_seat_indices.rotate(
                    -active_seat_indices.index(self.button_index) - 1,
                )

            for i in self.seat_indices:
                if i in active_seat_indices:
                    self.player_indices[i] = active_seat_indices.index(i)
                else:
                    self.player_indices[i] = None

            starting_stacks = []

            for i in active_seat_indices:
                starting_stack = self.starting_stacks[i]

                assert starting_stack is not None

                starting_stacks.append(starting_stack)

            self.state = self._create_state(starting_stacks)
        else:
            for i in self.seat_indices:
                self.player_indices[i] = None

            self.button_index = None

    def _create_state(self, starting_stacks: list[int]) -> State:
        return State(
            (),
            self.deck,
            self.hand_types,
            self.streets,
            self.betting_structure,
            self.ante_trimming_status,
            self.raw_antes,
            self.raw_blinds_or_straddles,
            self.bring_in,
            starting_stacks,
            len(starting_stacks),
        )

    _scheduler: Scheduler = field(init=False, default_factory=Scheduler)

    def run(self) -> None:
        self._scheduler.run()

    def stop(self) -> None:
        self._scheduler.stop()

    def _call(
            self,
            timeout: float,
            function: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> None:

        def nested_function() -> None:
            try:
                operation = function(*args, **kwargs)

                self._update()
                self.callback(self, operation)
            except:  # noqa: E722
                warn(format_exc())

        self._scheduler.schedule(timeout, nested_function)

    _counter: int = field(init=False, default=0)
    _counter_lock: Lock = field(init=False, default_factory=Lock)

    def _call_state(
            self,
            player_name: str | None,
            timeout: float,
            function: Callable[..., Operation | None],
            *args: Any,
            **kwargs: Any,
    ) -> None:

        def nested_function(count: int) -> Operation | None:

            with self._counter_lock:
                if count != self._counter:
                    raise ValueError('counter check failed')

            if self.state is None:
                raise ValueError('state does not exist')

            if player_name is None:
                if (
                        self.turn_index is not None
                        and self.state.showdown_index is None
                ):
                    idle_player_name = (
                        self.player_names[self.get_seat_index(self.turn_index)]
                    )

                    assert idle_player_name is not None

                    self._deactivate(idle_player_name)
            else:
                self._activate(player_name)

                if (
                        self.player_indices[self.get_seat_index(player_name)]
                        != self.turn_index
                ):
                    raise ValueError('player not in action')

            if (
                    self.turn_index is not None
                    and self.state.showdown_index is None
            ):
                seat_index = self.get_seat_index(self.turn_index)
                active_timestamp = self.active_timestamps[seat_index]
                timebank = self.timebanks[seat_index]

                assert active_timestamp is not None
                assert timebank is not None

                timebank_decrement = (
                    (datetime.now() - active_timestamp).total_seconds()
                )
                self.timebanks[seat_index] = max(
                    0,
                    timebank - timebank_decrement,
                )

            operation = function(self.state, *args, **kwargs)

            for i in self.seat_indices:
                self.active_timestamps[i] = None

            if (
                    self.turn_index is not None
                    and self.state.showdown_index is None
            ):
                seat_index = self.get_seat_index(self.turn_index)
                self.active_timestamps[seat_index] = datetime.now()

            with self._counter_lock:
                self._counter += 1

            return operation

        with self._counter_lock:
            self._call(timeout, nested_function, self._counter)

    def _update(self) -> None:
        if self.state is None or not self.state.status:
            for i in self.seat_indices:
                if self.is_kickable(i):
                    self.player_names[i] = None
                    self.player_indices[i] = None
                    self.starting_stacks[i] = None
                    self.buy_in_rebuy_top_off_or_rat_holing_amounts[i] = None
                    self.active_timestamps[i] = None
                    self.inactive_timestamps[i] = None
                    self.timebanks[i] = None

            self._call(self.play_timeout, self._play)
        else:
            if self.state.can_post_ante():
                self._call_state(
                    None,
                    self.ante_posting_timeout,
                    State.post_ante,
                )
            elif self.state.can_collect_bets():
                self._call_state(
                    None,
                    self.bet_collection_timeout,
                    State.collect_bets,
                )
            elif self.state.can_post_blind_or_straddle():
                self._call_state(
                    None,
                    self.blind_or_straddle_posting_timeout,
                    State.post_blind_or_straddle,
                )
            elif self.state.can_burn_card():
                self._call_state(
                    None,
                    self.card_burning_timeout,
                    State.burn_card,
                )
            elif self.state.can_deal_hole():
                self._call_state(
                    None,
                    self.hole_dealing_timeout,
                    State.deal_hole,
                )
            elif self.state.can_deal_board():
                self._call_state(
                    None,
                    self.board_dealing_timeout,
                    State.deal_board,
                )
            elif self.state.can_kill_hand():
                self._call_state(
                    None,
                    self.hand_killing_timeout,
                    State.kill_hand,
                )
            elif self.state.can_push_chips():
                self._call_state(
                    None,
                    self.chips_pushing_timeout,
                    State.push_chips,
                )
            elif self.state.can_pull_chips():
                self._call_state(
                    None,
                    self.chips_pulling_timeout,
                    State.pull_chips,
                )

            if self.turn_index is not None:
                seat_index = self.get_seat_index(self.turn_index)
                timebank = self.timebanks[seat_index]

                assert timebank is not None

                if self.is_active(seat_index):
                    timeout = None
                else:
                    timeout = self.skip_timeout

                if self.state.can_stand_pat_or_discard():
                    if timeout is None:
                        timeout = self.standing_pat_timeout + timebank

                    self._call_state(None, timeout, State.stand_pat_or_discard)
                elif self.state.can_fold():
                    if timeout is None:
                        timeout = self.folding_timeout + timebank

                    self._call_state(None, timeout, State.fold)
                elif self.state.can_check_or_call():
                    if timeout is None:
                        timeout = self.checking_timeout + timebank

                    self._call_state(None, timeout, State.check_or_call)
                elif self.state.can_post_bring_in():
                    if timeout is None:
                        timeout = self.bring_in_posting_timeout + timebank

                    self._call_state(None, timeout, State.post_bring_in)
                elif self.state.can_show_or_muck_hole_cards():
                    if timeout is None:
                        timeout = (
                            self.hole_cards_showing_or_mucking_timeout
                            + timebank
                        )

                    self._call_state(
                        None,
                        timeout,
                        State.show_or_muck_hole_cards,
                    )
                else:
                    raise AssertionError
