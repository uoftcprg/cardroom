from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field, KW_ONLY
from functools import partial
from itertools import chain
from math import pi
from typing import overload, TypeVar

from pokerkit import Card, CompletionBettingOrRaisingTo, HandHistory

from cardroom.table import Table

_T = TypeVar('_T')


@dataclass
class Configuration:
    _: KW_ONLY

    background_color: str = 'gray'

    table_border_color: str = 'saddlebrown'
    table_felt_color: str = 'seagreen'
    table_x: float = 0
    table_y: float = 0
    table_outer_width: float = 0.6
    table_outer_height: float = 0.35
    table_inner_width: float = 0.55
    table_inner_height: float = 0.3

    button_color: str = 'white'
    button_angle: float = pi / 24
    button_ring_width: float = 0.5
    button_ring_height: float = 0.25
    button_diameter: float = 0.035
    button_text_color: str = 'black'
    button_text_style: str = 'bold'
    button_text_font: str = 'sans'
    button_text_size: float = 0.025
    button_text: str = 'B'

    board_x: float = 0
    board_y: float = -0.05
    board_width: float = 0.3
    board_height: float = 0.025
    board_radius: float = 0.0125
    board_color: str = 'black'
    board_pot_text: str = 'Pot: '
    board_pot_text_color: str = 'white'
    board_pot_text_style: str = 'bold'
    board_pot_text_font: str = 'sans'
    board_pot_text_size: float = 0.02
    board_card_margin: float = 0.0025
    board_card_height: float = 0.06
    board_card_radius: float = 0.005
    board_card_color: str = 'white'
    board_card_text_style: str = 'bold'
    board_card_text_font: str = 'sans'
    board_card_text_size: float = 0.025

    bet_ring_width: float = 0.425
    bet_ring_height: float = 0.175
    bet_angle: float = 0
    bet_box_color: str = 'black'
    bet_box_x_padding: float = 0.025
    bet_box_height: float = 0.025
    bet_box_radius: float = 0.0125
    bet_text_style: str = 'bold'
    bet_text_color: str = 'white'
    bet_text_font: str = 'sans'
    bet_text_size: float = 0.02

    seat_ring_width: float = 0.8
    seat_ring_height: float = 0.55
    seat_angle: float = 0

    hole_x: float = 0
    hole_y: float = 0
    hole_width: float = 0.225
    hole_height: float = 0.03
    hole_radius: float = 0.005
    hole_color: str = 'black'
    hole_card_margin: float = 0.003
    hole_card_height: float = 0.05
    hole_card_radius: float = 0.004
    hole_card_color: str = 'white'
    hole_card_text_style: str = 'bold'
    hole_card_text_font: str = 'sans'
    hole_card_text_size: float = 0.025

    name_x: float = 0
    name_y: float = 0
    name_box_width: float = 0.225
    name_box_height: float = 0.03
    name_box_radius: float = 0
    name_box_color: str = 'darkblue'
    name_text_style: str = 'bold'
    name_text_color: str = 'white'
    name_text_font: str = 'sans'
    name_text_size: float = 0.02

    stack_x: float = 0
    stack_y: float = -0.03
    stack_box_width: float = 0.225
    stack_box_height: float = 0.03
    stack_box_radius: float = 0
    stack_box_color: str = 'black'
    stack_text_style: str = 'bold'
    stack_text_color: str = 'white'
    stack_text_font: str = 'sans'
    stack_text_size: float = 0.02

    previous_action_x: float = 0
    previous_action_y: float = -0.06
    previous_action_box_width: float = 0.225
    previous_action_box_height: float = 0.03
    previous_action_box_radius: float = 0
    previous_action_box_color: str = 'darkgray'
    previous_action_text_style: str = 'bold'
    previous_action_text_color: str = 'black'
    previous_action_text_font: str = 'sans'
    previous_action_text_size: float = 0.02

    club_color: str = 'green'
    diamond_color: str = 'blue'
    heart_color: str = 'red'
    spade_color: str = 'black'
    unknown_color: str = 'white'

    shifter_timeout: float = 0.25
    watchdog_timeout: float = 1

    frame_rate: float = 1000


@dataclass
class Data:
    _: KW_ONLY
    names: list[str | None] = field(default_factory=list)
    button: int | None = None
    bets: list[int | None] = field(default_factory=list)
    stacks: list[int | None] = field(default_factory=list)
    pots: list[int] = field(default_factory=list)
    holes: list[list[Card] | None] = field(default_factory=list)
    hole_statuses: list[bool] = field(default_factory=list)
    board: list[Card] = field(default_factory=list)
    board_count: int = 0
    previous_action: tuple[int, str] | None = None
    actor: int | None = None
    join: list[int] | None = None
    leave: bool = False
    sit_out: bool = False
    be_back: bool = False
    buy_rebuy_top_off_or_rat_hole: tuple[int, int] | None = None
    stand_pat_or_discard: list[Card] | None = None
    fold: bool = False
    check_or_call: int | None = None
    post_bring_in: int | None = None
    complete_bet_or_raise_to: tuple[bool, bool, int, int] | None = None
    show_or_muck_hole_cards: bool | None = None

    @classmethod
    def from_table(cls, table: Table) -> dict[str, Data]:
        button = None if table.button is None else table.button.seat_index
        hole_statuses = list[bool]()

        for street in table.game.streets:
            hole_statuses.extend(street.hole_dealing_statuses)

        if table.state is None:
            pots = []
            board = []
        else:
            pots = [pot.amount for pot in table.state.pots]
            board = table.state.board_cards.copy()

        board_count = table.game.max_board_card_count
        previous_action = None
        actor = None
        names = []
        bets = list[int | None]()
        stacks = list[int | None]()

        for seat in table.seats:
            names.append(seat.user)

            if seat.player_index is None or table.state is None:
                bets.append(None)
                stacks.append(seat.starting_stack)
            else:
                bets.append(table.state.bets[seat.player_index])
                stacks.append(table.state.stacks[seat.player_index])

                if (
                        (
                            table.state.stander_pat_or_discarder_index
                            == seat.player_index
                        )
                        or table.state.actor_index == seat.player_index
                        or table.state.showdown_index == seat.player_index
                ):
                    actor = seat.index

        data = {}

        for user in chain(table.users, ('',)):
            holes = list[list[Card] | None]()

            if table.can_join(user):
                join = list(
                    filter(partial(table.can_join, user), table.seat_indices),
                )
            else:
                join = None

            leave = table.can_leave(user)
            sit_out = table.can_sit_out(user)
            be_back = table.can_be_back(user)

            if table.can_buy_rebuy_top_off_or_rat_hole(user):
                buy_rebuy_top_off_or_rat_hole = (
                    table.min_starting_stack,
                    table.max_starting_stack,
                )
            else:
                buy_rebuy_top_off_or_rat_hole = None

            stand_pat_or_discard = None
            fold = False
            check_or_call = None
            post_bring_in = None
            complete_bet_or_raise_to = None
            show_or_muck_hole_cards = None
            seat_or_none = table.get_seat_or_none(user)

            if seat_or_none is not None and seat_or_none is table.acting_seat:
                assert table.state is not None

                if table.state.can_stand_pat_or_discard():
                    assert (
                        table.state.stander_pat_or_discarder_index
                        is not None
                    )

                    stand_pat_or_discard = list(
                        table.state.get_down_cards(
                            table.state.stander_pat_or_discarder_index,
                        ),
                    )

                if table.state.can_fold():
                    fold = True

                if table.state.can_check_or_call():
                    check_or_call = table.state.checking_or_calling_amount

                if table.state.can_post_bring_in():
                    post_bring_in = table.state.bring_in

                if table.state.can_complete_bet_or_raise_to():
                    assert (
                        table.state.min_completion_betting_or_raising_to_amount
                        is not None
                    )
                    assert (
                        table.state.max_completion_betting_or_raising_to_amount
                        is not None
                    )

                    complete_bet_or_raise_to = (
                        (
                            table.state.street_index == 0
                            and table.state.bring_in > 0
                            and (
                                CompletionBettingOrRaisingTo
                                not in set(map(type, table.state.operations))
                            )
                        ),
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

                if table.state.can_show_or_muck_hole_cards():
                    assert table.state.showdown_index is not None

                    show_or_muck_hole_cards = table.state.can_win_now(
                        table.state.showdown_index,
                    )

            for seat in table.seats:
                if seat.player_status:
                    assert seat.player_index is not None
                    assert table.state is not None

                    hole_cards = list[Card]()

                    for card, status in zip(
                            table.state.hole_cards[seat.player_index],
                            table.state.hole_card_statuses[seat.player_index],
                    ):
                        if status or user == seat.user:
                            hole_cards.append(card)
                        else:
                            hole_cards.extend(Card.parse('??'))

                    holes.append(hole_cards)
                else:
                    holes.append(None)

            data[user] = Data(
                names=names,
                button=button,
                bets=bets,
                stacks=stacks,
                pots=pots,
                holes=holes,
                hole_statuses=hole_statuses,
                board=board,
                board_count=board_count,
                previous_action=previous_action,
                actor=actor,
                join=join,
                leave=leave,
                sit_out=sit_out,
                be_back=be_back,
                buy_rebuy_top_off_or_rat_hole=buy_rebuy_top_off_or_rat_hole,
                stand_pat_or_discard=stand_pat_or_discard,
                fold=fold,
                check_or_call=check_or_call,
                post_bring_in=post_bring_in,
                complete_bet_or_raise_to=complete_bet_or_raise_to,
                show_or_muck_hole_cards=show_or_muck_hole_cards,
            )

        return data

    @classmethod
    def from_hand_history(cls, hand_history: HandHistory) -> Iterator[Data]:

        @overload
        def p2s(players: int) -> int:
            ...

        @overload
        def p2s(players: Iterable[_T]) -> list[_T | None]:
            ...

        def p2s(players: int | Iterable[_T]) -> int | list[_T | None]:
            if isinstance(players, int):
                return indices[players]

            seats: list[_T | None] = [None] * count

            for i, player in enumerate(players):
                seats[indices[i]] = player

            return seats

        game = hand_history.create_game()

        if hand_history.seat_count is not None:
            count = hand_history.seat_count
        elif hand_history.seats is not None:
            count = max(hand_history.seats)
        else:
            count = len(hand_history.starting_stacks)

        if hand_history.seats is None:
            indices = list(range(count))
        else:
            indices = [seat - 1 for seat in hand_history.seats]

        if hand_history.players is None:
            names = p2s(f'p{i}' for i in range(1, count + 1))
        else:
            names = p2s(hand_history.players)

        if game.button_status:
            button = p2s(len(hand_history.starting_stacks) - 1)
        else:
            button = None

        for state, action in hand_history.iter_state_actions():
            bets = p2s(state.bets)

            if state.status or hand_history.finishing_stacks is None:
                stacks = p2s(state.stacks)
            else:
                stacks = p2s(hand_history.finishing_stacks)

            pots = [pot.amount for pot in state.pots]

            if not pots:
                pots.append(0)

            holes = p2s(map(list.copy, state.hole_cards))

            for i, hole in enumerate(holes):
                if not hole:
                    holes[i] = None

            hole_statuses = list[bool]()

            for street in game.streets:
                hole_statuses.extend(street.hole_dealing_statuses)

            board = state.board_cards.copy()
            board_count = game.max_board_card_count
            operation = state.operations[-1] if state.operations else None

            if (
                    action is not None
                    and operation is not None
                    and hasattr(operation, 'player_index')
            ):
                previous_action = p2s(operation.player_index), action
            else:
                previous_action = None

            if state.stander_pat_or_discarder_index is not None:
                actor = p2s(state.stander_pat_or_discarder_index)
            elif state.actor_index is not None:
                actor = p2s(state.actor_index)
            elif state.showdown_index is not None:
                actor = p2s(state.showdown_index)
            else:
                actor = None

            yield Data(
                names=names,
                button=button,
                bets=bets,
                stacks=stacks,
                pots=pots,
                holes=holes,
                hole_statuses=hole_statuses,
                board=board,
                board_count=board_count,
                previous_action=previous_action,
                actor=actor,
            )
