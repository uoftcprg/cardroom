from __future__ import annotations

from collections.abc import Iterable, Iterator
from collections import deque
from dataclasses import dataclass, field, KW_ONLY
from datetime import datetime
from math import pi
from typing import ClassVar, overload, TypeVar

from pokerkit import Card, HandHistory, parse_action, State

_T = TypeVar('_T')


@dataclass
class Settings:
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
    board_card_text_size: str = 0.025

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
    hole_color: float = 'black'
    hole_card_margin: float = 0.003
    hole_card_height: float = 0.05
    hole_card_radius: float = 0.004
    hole_card_color: str = 'white'
    hole_card_text_style: str = 'bold'
    hole_card_text_font: str = 'sans'
    hole_card_text_size: str = 0.025

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
    timestamps: list[datetime] | None = None

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

        state: State | None = None
        actions = deque(hand_history.actions)

        while state is None or state.status:
            if state is None:
                state = hand_history.create_state()
                status = False
            else:
                status = True

            previous_action = None
            action = None

            while status:
                status = False

                if state.can_post_ante():
                    state.post_ante()
                elif state.can_post_blind_or_straddle():
                    state.post_blind_or_straddle()
                elif state.can_collect_bets():
                    state.collect_bets()
                elif state.can_burn_card():
                    state.burn_card('??')

                    status = True
                elif state.can_kill_hand():
                    state.kill_hand()
                elif state.can_push_chips():
                    state.push_chips()
                elif state.can_pull_chips():
                    state.pull_chips()
                else:
                    action = actions.popleft()

                    parse_action(state, action)

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
                timestamps=None,
            )
