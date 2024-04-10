from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, KW_ONLY, replace
from datetime import datetime
from itertools import chain
from typing import Literal, TypeVar

from pokerkit import Card, HandHistory, Poker

from cardroom.table import Table

_T = TypeVar('_T')


@dataclass(frozen=True)
class Seat:
    _: KW_ONLY
    user: str
    button: bool
    bet: int | None
    stack: int | None
    hole: tuple[Card, ...]
    timestamp: tuple[()] | tuple[datetime] | tuple[datetime, datetime]
    active: bool
    turn: bool

    @classmethod
    def from_table(
            cls,
            table: Table,
            timestamp: tuple[()] | tuple[datetime] | tuple[datetime, datetime],
    ) -> dict[str, tuple[Seat, ...]]:
        seats: dict[str, list[Seat]] = {
            user: [] for user in chain(table.users, ('',))
        }

        for seat in table.seats:
            user = seat.user or ''
            button = seat is table.button.seat
            active = seat.active_status
            hole: tuple[Card, ...]
            censored_hole: tuple[Card, ...]

            if not seat.player_status:
                bet = None
                stack = seat.starting_stack
                hole = ()
                censored_hole = ()
                turn = False
            else:
                assert table.state is not None
                assert seat.player_index is not None

                bet = table.state.bets[seat.player_index]
                stack = table.state.stacks[seat.player_index]
                hole = tuple(table.state.hole_cards[seat.player_index])
                censored_hole = tuple(
                    table.state.get_censored_hole_cards(seat.player_index),
                )
                turn = seat is table.turn_seat

            uncensored_seat = Seat(
                user=user,
                button=button,
                bet=bet,
                stack=stack,
                hole=hole,
                timestamp=timestamp if turn else (),
                active=active,
                turn=turn,
            )
            censored_seat = replace(uncensored_seat, hole=censored_hole)

            for key, value in seats.items():
                value.append(uncensored_seat if user == key else censored_seat)

        return dict(zip(seats.keys(), map(tuple, seats.values())))

    @classmethod
    def from_hand_history(
            cls,
            hand_history: HandHistory,
    ) -> Iterator[tuple[Seat, ...]]:
        timestamp = ()
        active = True

        for state in hand_history:
            seats = []

            for i in state.player_indices:
                if hand_history.players is None:
                    user = ''
                else:
                    user = hand_history.players[i]

                button = i == state.player_count - 1
                bet = state.bets[i]
                stack = state.stacks[i]
                hole = tuple(state.hole_cards[i])
                turn = i == state.turn_index
                seat = Seat(
                    user=user,
                    button=button,
                    bet=bet,
                    stack=stack,
                    hole=hole,
                    timestamp=timestamp,
                    active=active,
                    turn=turn,
                )

                seats.append(seat)

            yield tuple(seats)


@dataclass(frozen=True)
class Game:
    _: KW_ONLY
    hole: tuple[tuple[bool, ...], ...]
    board: tuple[int, ...]
    draw: tuple[bool, ...]

    @classmethod
    def from_game(cls, game: Poker) -> Game:
        hole = tuple(street.hole_dealing_statuses for street in game.streets)
        board = tuple(street.board_dealing_count for street in game.streets)
        draw = tuple(street.draw_status for street in game.streets)

        return Game(hole=hole, board=board, draw=draw)


@dataclass(frozen=True)
class Action:
    _: KW_ONLY
    j: tuple[int, ...] | None
    l: Literal[True] | None
    s: Literal[True] | None
    b: Literal[True] | None
    brtr: tuple[int, int] | None
    sd: Literal[True] | None
    f: Literal[True] | None
    cc: int | None
    pb: int | None
    cbr: tuple[bool, bool, int, int] | None
    sm: bool | None

    @classmethod
    def from_table(cls, table: Table) -> dict[str, Action]:
        actions = {}

        for user in chain(table.users, ('',)):
            if table.can_join(user):
                j = tuple(seat.index for seat in table.empty_seats)
            else:
                j = None

            l = table.can_leave(user) or None  # noqa: E741
            s = table.can_sit_out(user) or None
            b = table.can_be_back(user) or None

            if table.can_buy_rebuy_top_off_or_rat_hole(user):
                brtr = (
                    table.min_starting_stack,
                    table.max_starting_stack,
                )
            else:
                brtr = None

            if table.turn_seat is table.get_seat(user) is not None:
                assert table.state is not None

                sd = table.state.can_stand_pat_or_discard() or None
                f = table.state.can_fold() or None

                if table.state.can_check_or_call():
                    cc = table.state.checking_or_calling_amount
                else:
                    cc = None

                if table.state.can_post_bring_in():
                    pb = table.state.bring_in
                else:
                    pb = None

                if table.state.can_complete_bet_or_raise_to():
                    assert (
                        table.state.min_completion_betting_or_raising_to_amount
                        is not None
                    )
                    assert (
                        table.state.max_completion_betting_or_raising_to_amount
                        is not None
                    )

                    cbr = (
                        table.state.completion_status,
                        any(table.state.bets),
                        (
                            table
                            .state
                            .min_completion_betting_or_raising_to_amount
                        ),
                        (
                            table
                            .state
                            .max_completion_betting_or_raising_to_amount
                        ),
                    )
                else:
                    cbr = None

                if table.state.can_show_or_muck_hole_cards():
                    assert table.state.showdown_index is not None

                    sm = table.state.can_win_now(table.state.showdown_index)
                else:
                    sm = None
            else:
                sd = None
                f = None
                cc = None
                pb = None
                cbr = None
                sm = None

            actions[user] = Action(
                j=j,
                l=l,
                s=s,
                b=b,
                brtr=brtr,
                sd=sd,
                f=f,
                cc=cc,
                pb=pb,
                cbr=cbr,
                sm=sm,
            )

        return actions

    @classmethod
    def create_empty(self) -> Action:
        return Action(
            j=None,
            l=None,
            s=None,
            b=None,
            brtr=None,
            sd=None,
            f=None,
            cc=None,
            pb=None,
            cbr=None,
            sm=None,
        )


@dataclass(frozen=True)
class Frame:
    _: KW_ONLY
    seats: tuple[Seat, ...]
    pot: tuple[int, ...]
    board: tuple[Card, ...]
    game: Game
    action: Action
    history: str

    @classmethod
    def from_table(
            cls,
            table: Table,
            timestamp: tuple[()] | tuple[datetime] | tuple[datetime, datetime],
    ) -> dict[str, Frame]:
        seats = Seat.from_table(table, timestamp)
        pot: tuple[int, ...]
        board: tuple[Card, ...]

        if table.state is None:
            pot = ()
            board = ()
        else:
            pot = tuple(pot.amount for pot in table.state.pots)
            board = tuple(table.state.board_cards)

        game = Game.from_game(table.game)
        actions = Action.from_table(table)

        if table.state is None:
            history = ''
        else:
            hh = table.hand_history

            assert hh is not None

            history = hh.dumps()

        frames = {}

        for user in chain(table.users, ('',)):
            frames[user] = Frame(
                seats=seats[user],
                pot=pot,
                board=board,
                game=game,
                action=actions[user],
                history=history,
            )

        return frames

    @classmethod
    def from_hand_history(cls, hand_history: HandHistory) -> Iterator[Frame]:
        game = Game.from_game(hand_history.create_game())
        action = Action.create_empty()
        history = hand_history.dumps()

        for seats, state in zip(
                Seat.from_hand_history(hand_history),
                hand_history,
        ):
            pot = tuple(pot.amount for pot in state.pots)
            board = tuple(state.board_cards)

            yield Frame(
                seats=seats,
                pot=pot,
                board=board,
                game=game,
                action=action,
                history=history,
            )
