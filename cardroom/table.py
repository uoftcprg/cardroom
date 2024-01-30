from __future__ import annotations

from collections.abc import Iterator
from collections import deque
from dataclasses import dataclass, field
from random import choice
from warnings import warn

from pokerkit import Poker, State


@dataclass
class Button:
    table: Table
    seat_index: int | None = field(default=None, init=False)
    user: str | None = field(default=None, init=False)

    @property
    def seat(self) -> Seat | None:
        if self.seat_index is None:
            seat = None
        else:
            seat = self.table.seats[self.seat_index]

        return seat

    def step(self) -> deque[int]:
        seat_indices = deque[int]()

        if self.table.game.button_status:
            if (
                    self.user is None
                    or self.table.get_seat_or_none(self.user) is not self.seat
            ):
                self.seat_index = None

            if self.seat_index is None:
                self.seat_index = choice(
                    tuple(self.table.ready_or_postable_indices),
                )

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

            self.user = self.seat.user
            seats = deque(self.table.seats)

            seats.rotate(-self.seat_index - 1)

            for seat in seats:
                if seat.ready_status:
                    seat_indices.append(seat.index)
        else:
            self.seat_index = None
            self.user = None

            for seat in self.table.seats:
                seat.wait_status = False

            seat_indices.extend(self.table.ready_indices)

        return seat_indices


@dataclass
class Seat:
    table: Table
    user: str | None = field(default=None, init=False)
    player_index: int | None = field(default=None, init=False)
    active_status: bool = field(default=False, init=False)
    wait_status: bool = field(default=False, init=False)
    starting_stack: int | None = field(default=None, init=False)

    @property
    def index(self) -> int:
        return next(
            i for i, seat in enumerate(self.table.seats) if self is seat
        )

    @property
    def user_status(self) -> bool:
        return self.user is not None

    @property
    def ready_or_postable_status(self) -> bool:
        return (
            self.user_status
            and self.active_status
            and self.starting_stack is not None
            and self.starting_stack > 0
        )

    @property
    def ready_status(self) -> bool:
        return self.ready_or_postable_status and not self.wait_status

    @property
    def player_status(self) -> bool:
        return self.player_index is not None


@dataclass
class Table:
    game: Poker
    seat_count: int
    min_starting_stack: int
    max_starting_stack: int
    button: Button = field(init=False)
    seats: list[Seat] = field(default_factory=list, init=False)
    state: State | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.button = Button(self)

        for _ in range(self.seat_count):
            self.seats.append(Seat(self))

    @property
    def seat_indices(self) -> range:
        return range(self.seat_count)

    @property
    def user_indices(self) -> Iterator[int]:
        for seat in self.seats:
            if seat.user_status:
                yield seat.index

    @property
    def user_seats(self) -> Iterator[Seat]:
        for i in self.user_indices:
            yield self.seats[i]

    @property
    def user_count(self) -> int:
        return len(tuple(self.user_indices))

    @property
    def ready_or_postable_indices(self) -> Iterator[int]:
        for seat in self.seats:
            if seat.ready_or_postable_status:
                yield seat.index

    @property
    def ready_or_postable_seats(self) -> Iterator[Seat]:
        for i in self.ready_or_postable_indices:
            yield self.seats[i]

    @property
    def ready_or_postable_count(self) -> int:
        return len(tuple(self.ready_or_postable_indices))

    @property
    def ready_indices(self) -> Iterator[int]:
        for seat in self.seats:
            if seat.ready_status:
                yield seat.index

    @property
    def ready_seats(self) -> Iterator[Seat]:
        for i in self.ready_indices:
            yield self.seats[i]

    @property
    def ready_count(self) -> int:
        return len(tuple(self.ready_indices))

    @property
    def users(self) -> Iterator[str]:
        for seat in self.seats:
            if seat.user_status:
                assert seat.user is not None

                yield seat.user

    @property
    def acting_seat(self) -> Seat | None:
        if self.state is not None:
            for seat in self.seats:
                if (
                        seat.player_status
                        and (
                            (
                                seat.player_index
                                == self.state.stander_pat_or_discarder_index
                            )
                            or seat.player_index == self.state.actor_index
                            or seat.player_index == self.state.showdown_index
                        )
                ):
                    return seat

        return None

    def get_seat(self, user: str) -> Seat:
        for seat in self.seats:
            if seat.user == user:
                return seat

        raise ValueError('user not found')

    def get_seat_or_none(self, user: str) -> Seat | None:
        try:
            seat = self.get_seat(user)
        except ValueError:
            seat = None

        return seat

    # game changing

    def verify_game_changing(self, game: Poker) -> None:
        if self.state is not None:
            raise ValueError('ongoing game')

    def can_change_game(self, game: Poker) -> bool:
        try:
            self.verify_game_changing(game)
        except ValueError:
            return False

        return True

    def change_game(self, game: Poker) -> None:
        self.verify_game_changing(game)

        self.game = game

    # state management

    def verify_state_construction(self) -> None:
        if self.state is not None and self.state.status:
            raise ValueError('state already constructed')
        elif self.ready_or_postable_count < 2:
            raise ValueError('not enough ready players')

    def can_construct_state(self) -> bool:
        try:
            self.verify_state_construction()
        except ValueError:
            return False

        return True

    def construct_state(self) -> None:
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
        if self.state is None:
            raise ValueError('state already destroyed')
        elif self.state.status:
            raise ValueError('state active')

    def can_destroy_state(self) -> bool:
        try:
            self.verify_state_destruction()
        except ValueError:
            return False

        return True

    def destroy_state(self) -> None:
        self.verify_state_destruction()

        assert self.state
        assert not self.state.status

        for seat in self.seats:
            if seat.player_status:
                assert seat.player_index is not None

                stack = self.state.stacks[seat.player_index]

                if seat.starting_stack is None:
                    seat.starting_stack = stack
                elif stack > seat.starting_stack:
                    warn('rat-holing')

            seat.player_index = None

            if not seat.starting_stack:
                seat.starting_stack = None

        self.state = None

    # player management

    def verify_joining(self, user: str, seat_index: int | None = None) -> None:
        for seat in self.seats:
            if seat.user == user:
                raise ValueError('user already joined')

        if seat_index is None:
            if len(tuple(self.users)) == self.seat_count:
                raise ValueError('full table')
        else:
            if seat_index not in self.seat_indices:
                raise ValueError('invalid seat index')
            elif self.seats[seat_index].user_status:
                raise ValueError('seat occupied')

    def can_join(self, user: str, seat_index: int | None = None) -> bool:
        try:
            self.verify_joining(user, seat_index)
        except ValueError:
            return False

        return True

    def join(self, user: str, seat_index: int) -> None:
        self.verify_joining(user, seat_index)

        seat = self.seats[seat_index]
        seat.user = user
        seat.player_index = None
        seat.active_status = True
        seat.wait_status = True
        seat.starting_stack = None

    def verify_leaving(self, user: str) -> Seat:
        seat = self.get_seat(user)

        if seat.player_status:
            raise ValueError('player in hand')

        return seat

    def can_leave(self, user: str) -> bool:
        try:
            self.verify_leaving(user)
        except ValueError:
            return False

        return True

    def leave(self, user: str) -> None:
        seat = self.verify_leaving(user)

        assert not seat.player_status

        seat.user = None
        seat.player_index = None
        seat.active_status = False
        seat.wait_status = False
        seat.starting_stack = None

    def verify_sitting_out(self, user: str) -> Seat:
        seat = self.get_seat(user)

        if not seat.active_status:
            raise ValueError('already deactivated')

        return seat

    def can_sit_out(self, user: str) -> bool:
        try:
            self.verify_sitting_out(user)
        except ValueError:
            return False

        return True

    def sit_out(self, user: str) -> None:
        seat = self.verify_sitting_out(user)
        seat.active_status = False

    def verify_being_back(self, user: str) -> Seat:
        seat = self.get_seat(user)

        if seat.active_status:
            raise ValueError('already activated')

        return seat

    def can_be_back(self, user: str) -> bool:
        try:
            self.verify_being_back(user)
        except ValueError:
            return False

        return True

    def be_back(self, user: str) -> None:
        seat = self.verify_being_back(user)
        seat.active_status = True

    def verify_buying_rebuying_topping_off_or_rat_holing(
            self,
            user: str,
            starting_stack: int | None = None,
    ) -> Seat:
        seat = self.get_seat(user)

        if not seat.active_status:
            raise ValueError('inactive user')

        if starting_stack is not None:
            if starting_stack < self.min_starting_stack:
                raise ValueError('below minimum starting stack')
            elif starting_stack > self.max_starting_stack:
                raise ValueError('above maximum starting stack')
            elif (
                    seat.starting_stack is not None
                    and seat.starting_stack > starting_stack
            ):
                warn('rat-holing')

        return seat

    def can_buy_rebuy_top_off_or_rat_hole(
            self,
            user: str,
            starting_stack: int | None = None,
    ) -> bool:
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
        seat = self.verify_buying_rebuying_topping_off_or_rat_holing(
            user,
            starting_stack,
        )
        seat.starting_stack = starting_stack
