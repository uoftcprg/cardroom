""":mod:`cardroom.table` implements classes related to poker tables.

This module simply encodes table logic that is time-agnostic. This
entails joining, leaving, and so on WITHOUT timeouts such as auto
check, fold, et cetera. Timings are implemented in
:mod:`cardroom.controller`.
"""

from __future__ import annotations

from collections.abc import Iterator
from collections import deque
from dataclasses import dataclass, field
from random import choice

from pokerkit import HandHistory, Poker, State

from cardroom.utilities import get_rat_holing_status


@dataclass
class Button:
    """The class for table buttons.

    Unlike its name, this class not only keeps track of button position
    but also determines who is eligible to play the next hand.

    As such, this instance is also relevant in stud games that do not
    use the button.
    """

    table: Table
    """The table the button is part of."""
    seat_index: int | None = field(default=None, init=False)
    """The seat index at which the button is placed in."""

    @property
    def seat(self) -> Seat | None:
        """Return the button's associated seat.

        If no seat is associated, ``None`` is returned.

        :return: The associated seat or ``None``.
        """
        if self.seat_index is None:
            seat = None
        else:
            seat = self.table.seats[self.seat_index]

        return seat

    def step(self) -> deque[int]:
        """Move or place the button and return the seats that contain
        the players of the next poker game, in order.

        :return: The ordered seat indices that can play the next hand.
        """
        seat_indices = deque[int]()

        if self.table.game.button_status:
            if self.seat_index is None:
                seat = choice(tuple(self.table.ready_or_postable_seats))
                self.seat_index = seat.index

                for seat in self.table.seats:
                    seat.wait_status = False
            else:
                seats = deque(self.table.seats)

                seats.rotate(-self.seat_index - 1)

                while not seats[0].ready_status:
                    seats[0].wait_status = False

                    seats.rotate(-1)

                self.seat_index = seats[0].index

            assert self.seat is not None

            seats = deque(self.table.seats)

            seats.rotate(-self.seat_index - 1)

            for seat in seats:
                if seat.ready_status:
                    seat_indices.append(seat.index)
        else:
            self.seat_index = None

            for seat in self.table.seats:
                seat.wait_status = False

            seat_indices.extend(seat.index for seat in self.table.ready_seats)

        return seat_indices


@dataclass
class Seat:
    """The class for table seats."""

    table: Table
    """The table the seat is part of."""
    user: str | None = field(default=None, init=False)
    """The user sitting in the seat (if any)."""
    player_index: int | None = field(default=None, init=False)
    """The player index of the seated player (if playing)."""
    active_status: bool = field(default=False, init=False)
    """The active status (``False`` if idle)."""
    wait_status: bool = field(default=False, init=False)
    """The wait status (``False`` if no need to wait before playing)."""
    starting_stack: int | None = field(default=None, init=False)
    """The starting stack override. When rebuying, buying in, etc., this
    attribute is updated to reflect the new desired value. If this is
    none, this attribute is overridden at the and of each hand to
    reflect the final stacks of the state (if involved in the hand).
    """

    @property
    def index(self) -> int:
        """Return the seat index (position).

        :return: The seat index.
        """
        return next(
            i for i, seat in enumerate(self.table.seats) if self is seat
        )

    @property
    def user_status(self) -> bool:
        """Return whether a user is seated in the seat.

        :return: The user status.
        """
        return self.user is not None

    @property
    def ready_or_postable_status(self) -> bool:
        """Return whether the seat is ready to play or ready after
        posting a post bet.

        A post bet is relevant when the person just joined the table but
        has to wait for the button to pass before being able to play. If
        they do not want to wait, they can pay the post bet (equivalent
        to the big blind) and begin play immediately.

        They do not need to pay the post bet in games without button
        like in stud games.

        :return: The ready (maybe after posting) status.
        """
        return (
            self.user_status
            and self.active_status
            and self.starting_stack is not None
            and self.starting_stack > 0
        )

    @property
    def ready_status(self) -> bool:
        """Return whether the seat is ready to play even without posting
        a post bet.

        Since the player does not need to pay the post bet, this means
        the player joined, waited for the button, and the button passed
        them, allowing them to begin play in the table. Or, they are
        playing non-button games like stud games.

        :return: The ready status.
        """
        return self.ready_or_postable_status and not self.wait_status

    @property
    def player_status(self) -> bool:
        """Return whether the user in the seat (if any) is involved
        in the ongoing game (if any).

        :return: The player stauts.
        """
        return self.player_index is not None


@dataclass
class Table:
    """The class for cardroom tables."""

    game: Poker
    """The game being played on the table."""
    seat_count: int
    """The number of seats in the table."""
    min_starting_stack: int
    """The minimum starting stack, buy-in amount, etc."""
    max_starting_stack: int
    """The maximum starting stack, buy-in amount, etc."""
    button: Button = field(init=False)
    """The table's button."""
    seats: list[Seat] = field(default_factory=list, init=False)
    """The table seats."""
    state: State | None = field(default=None, init=False)
    """The state of the game being played on the table (if ongoing)."""

    def __post_init__(self) -> None:
        self.button = Button(self)

        for _ in range(self.seat_count):
            self.seats.append(Seat(self))

    @property
    def seat_indices(self) -> range:
        """Return the table's seat indices.

        :return: The seat indices.
        """
        return range(self.seat_count)

    @property
    def empty_seats(self) -> Iterator[Seat]:
        """Yield the empty seats.

        :return: The empty seats.
        """
        for seat in self.seats:
            if not seat.user_status:
                yield seat

    @property
    def occupied_seats(self) -> Iterator[Seat]:
        """Yield the seated seats.

        :return: The seated seats.
        """
        for seat in self.seats:
            if seat.user_status:
                yield seat

    @property
    def ready_or_postable_seats(self) -> Iterator[Seat]:
        """Yield the ready or postable seats.

        On what being ready/postable means, please refer to
        :attr:`cardroom.table.Seat.ready_or_postable_status`.

        :return: The ready or postable seats.
        """
        for seat in self.seats:
            if seat.ready_or_postable_status:
                yield seat

    @property
    def ready_seats(self) -> Iterator[Seat]:
        """Yield the ready seats.

        On what being ready means, please refer to
        :attr:`cardroom.table.Seat.ready_status`.

        :return: The ready seats.
        """
        for seat in self.seats:
            if seat.ready_status:
                yield seat

    @property
    def users(self) -> Iterator[str]:
        """Yield the users.

        :return: The users.
        """
        for seat in self.occupied_seats:
            assert seat.user is not None

            yield seat.user

    @property
    def turn_seat(self) -> Seat | None:
        """Return the seat whose player is in turn to act.

        If this does not exist or is not applicable, ``None`` is
        returned.

        :return: The turn seat or ``None``.
        """
        if self.state is not None:
            for seat in self.seats:
                if (
                        seat.player_status
                        and seat.player_index == self.state.turn_index
                ):
                    return seat

        return None

    @property
    def player_seats(self) -> Iterator[Seat]:
        """Iterate through the seats that contain the players, in order.

        :return: The player seats.
        """
        if self.state is not None:
            seats = {seat.player_index: seat for seat in self.seats}

            for i in self.state.player_indices:
                yield seats[i]

    @property
    def hand_history(self) -> HandHistory | None:
        """Return the hand history of active state, if any.

        :return: The hand history or ``None``.
        """
        if self.state is None:
            hh = None
        else:
            hh = HandHistory.from_game_state(
                self.game,
                self.state,
                seats=[seat.index for seat in self.player_seats],
                players=[seat.user for seat in self.player_seats],
            )

        return hh

    def get_seat(self, user: str) -> Seat | None:
        """Lookup the seat of the user.

        If none is found, ``None`` is returned.

        :return: The seat of the user or ``None``.
        """
        for seat in self.seats:
            if seat.user == user:
                return seat

        return None

    # game changing

    def verify_game_changing(self, game: Poker) -> None:
        """Verify the game changing operation.

        :param game: The changed game.
        :return: ``None``.
        """
        if self.state is not None:
            raise ValueError('There is currently an ongoing game.')

    def can_change_game(self, game: Poker) -> bool:
        """Query the validity of the game changing operation.

        :param game: The changed game.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_game_changing(game)
        except ValueError:
            return False

        return True

    def change_game(self, game: Poker) -> None:
        """Perform the game changing operation.

        :param game: The changed game.
        :return: ``None``.
        """
        self.verify_game_changing(game)

        self.game = game

    # state management

    def verify_state_construction(self) -> None:
        """Verify the state construction operation.

        :return: ``None``.
        """
        if self.state is not None:
            raise ValueError(
                'There is currently a state associated with this table.',
            )
        elif len(tuple(self.ready_or_postable_seats)) < 2:
            raise ValueError(
                'There is currently not enough player to start a game.',
            )

    def can_construct_state(self) -> bool:
        """Query the validity of the state construction operation.

        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_state_construction()
        except ValueError:
            return False

        return True

    def construct_state(self) -> None:
        """Perform the state construction operation.

        :return: ``None``.
        """
        self.verify_state_construction()

        seat_indices = self.button.step()
        starting_stacks = []

        for i, j in enumerate(seat_indices):
            self.seats[j].player_index = i
            starting_stack = self.seats[j].starting_stack

            assert starting_stack is not None

            starting_stacks.append(starting_stack)

            self.seats[j].starting_stack = None

        player_count = len(seat_indices)
        self.state = self.game(starting_stacks, player_count)

    def verify_state_destruction(self) -> None:
        """Verify the state destruction operation.

        :return: ``None``.
        """
        if self.state is None:
            raise ValueError('There is no state to destroy.')
        elif self.state.status:
            raise ValueError(
                'The current state is active and therefore cannot be changed.',
            )

    def can_destroy_state(self) -> bool:
        """Query the validity of the state destruction operation.

        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_state_destruction()
        except ValueError:
            return False

        return True

    def destroy_state(self) -> None:
        """Perform the state destruction operation.

        :return: ``None``.
        """
        self.verify_state_destruction()

        assert self.state is not None
        assert not self.state.status

        for seat in self.seats:
            if seat.player_status:
                assert seat.player_index is not None

                stack = self.state.stacks[seat.player_index]

                if (
                        seat.starting_stack is not None
                        and stack > seat.starting_stack
                        and not get_rat_holing_status()
                ):
                    seat.starting_stack = None

                if seat.starting_stack is None:
                    seat.starting_stack = stack

            seat.player_index = None

            if not seat.starting_stack:
                seat.starting_stack = None

        self.state = None

    # player management

    def verify_joining(self, user: str, seat_index: int | None = None) -> None:
        """Verify the joining operation.

        :param user: The user joining the table.
        :param seat_index: The seat index at which the user is joining.
        :return: ``None``.
        """
        if self.get_seat(user) is not None:
            raise ValueError('The user has already joined.')
        elif seat_index is None:
            if not tuple(self.empty_seats):
                raise ValueError('The table is currently full.')
        else:
            if seat_index not in self.seat_indices:
                raise ValueError('The seat index is not valid.')
            elif (
                    seat_index
                    not in tuple(seat.index for seat in self.empty_seats)
            ):
                raise ValueError('The desired seat is already occupied.')

    def can_join(self, user: str, seat_index: int | None = None) -> bool:
        """Query the validity of the joining operation.

        :param user: The user joining the table.
        :param seat_index: The seat index at which the user is joining.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_joining(user, seat_index)
        except ValueError:
            return False

        return True

    def join(self, user: str, seat_index: int) -> None:
        """Perform the joining operation.

        :param user: The user joining the table.
        :param seat_index: The seat index at which the user is joining.
        :return: ``None``.
        """
        self.verify_joining(user, seat_index)

        seat = self.seats[seat_index]
        seat.user = user
        seat.player_index = None
        seat.active_status = True
        seat.wait_status = True
        seat.starting_stack = None

    def verify_leaving(self, user: str) -> Seat:
        """Verify the leaving operation.

        :param user: The user leaving the table.
        :return: The seat the user is in.
        """
        seat = self.get_seat(user)

        if seat is None:
            raise ValueError(f'The user {user} is not seated.')
        elif seat.player_status:
            raise ValueError(
                f'The user {user} is in the hand and therefore cannot leave.',
            )

        return seat

    def can_leave(self, user: str) -> bool:
        """Query the validity of the leaving operation.

        :param user: The user leaving the table.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_leaving(user)
        except ValueError:
            return False

        return True

    def leave(self, user: str) -> None:
        """Perform the leaving operation.

        :param user: The user leaving the table.
        :return: ``None``.
        """
        seat = self.verify_leaving(user)

        assert not seat.player_status

        seat.user = None
        seat.player_index = None
        seat.active_status = False
        seat.wait_status = False
        seat.starting_stack = None

    def verify_sitting_out(self, user: str) -> Seat:
        """Verify the sitting out operation.

        :param user: The user sitting out.
        :return: The seat the user is in.
        """
        seat = self.get_seat(user)

        if seat is None:
            raise ValueError(f'The user {user} is not seated.')
        elif not seat.active_status:
            raise ValueError(f'The user {user} has already sit out.')

        return seat

    def can_sit_out(self, user: str) -> bool:
        """Query the validity of the sitting out operation.

        :param user: The user sitting out.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_sitting_out(user)
        except ValueError:
            return False

        return True

    def sit_out(self, user: str) -> None:
        """Perform the sitting out operation.

        Sitting out is akin to becoming idle or away from keyboard
        (AFK).

        :param user: The user sitting out.
        :return: ``None``.
        """
        seat = self.verify_sitting_out(user)
        # TODO: seat.active_status = False

    def verify_being_back(self, user: str) -> Seat:
        """Verify the being back operation.

        :param user: The user being back.
        :return: The seat the user is in.
        """
        seat = self.get_seat(user)

        if seat is None:
            raise ValueError(f'The user {user} is not seated.')
        elif seat.active_status:
            raise ValueError(f'The user {user} is already back.')

        return seat

    def can_be_back(self, user: str) -> bool:
        """Query the validity of the sitting out operation.

        :param user: The user sitting out.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_being_back(user)
        except ValueError:
            return False

        return True

    def be_back(self, user: str) -> None:
        """Perform the being back operation.

        Being back is akin to resuming or saying "I'm back".

        :param user: The user being back.
        :return: ``None``.
        """
        seat = self.verify_being_back(user)
        seat.active_status = True

    def verify_buying_rebuying_topping_off_or_rat_holing(
            self,
            user: str,
            starting_stack: int | None = None,
    ) -> Seat:
        """Verify the stack overriding operation.

        :param user: The user overriding their stack.
        :param starting_stack: The new desired stack amount.
        :return: The seat the user is in.
        """
        seat = self.get_seat(user)

        if seat is None:
            raise ValueError(f'The user {user} is not seated.')

        if starting_stack is not None:
            if starting_stack < self.min_starting_stack:
                raise ValueError(
                    (
                        f'The amount {starting_stack} is below minimum'
                        f' starting stack {self.min_starting_stack}.'
                    ),
                )
            elif starting_stack > self.max_starting_stack:
                raise ValueError(
                    (
                        f'The amount {starting_stack} is above maximum'
                        f' starting stack {self.max_starting_stack}.'
                    ),
                )
            elif (
                    seat.starting_stack is not None
                    and seat.starting_stack > starting_stack
                    and not get_rat_holing_status()
            ):
                raise ValueError(
                    (
                        f'The user {user} is rat-holing to {starting_stack}'
                        f' from {seat.starting_stack}.'
                    ),
                )

        return seat

    def can_buy_rebuy_top_off_or_rat_hole(
            self,
            user: str,
            starting_stack: int | None = None,
    ) -> bool:
        """Query the validity of the stack overriding operation.

        :param user: The user overriding their stack.
        :param starting_stack: The new desired stack amount.
        :return: ``True`` if valid, else ``False``.
        """
        try:
            self.verify_buying_rebuying_topping_off_or_rat_holing(
                user,
                starting_stack,
            )
        except ValueError:
            return False

        return True

    def buy_rebuy_top_off_or_rat_hole(
            self,
            user: str,
            starting_stack: int,
    ) -> None:
        """Perform the stack overriding operation.

        :param user: The user overriding their stack.
        :param starting_stack: The new desired stack amount.
        :return: ``None``.
        """
        seat = self.verify_buying_rebuying_topping_off_or_rat_holing(
            user,
            starting_stack,
        )
        seat.starting_stack = starting_stack
