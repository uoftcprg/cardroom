from __future__ import annotations

from collections.abc import Iterable, Iterator
from collections import deque
from dataclasses import dataclass, KW_ONLY
from datetime import datetime
from math import pi
from typing import overload, TypeVar

from pokerkit import Card, HandHistory, parse_action, State

_T = TypeVar('_T')


@dataclass
class Settings:
    _: KW_ONLY
    background_color: str = 'Gray'

    inner_table_color: str = 'SeaGreen'
    inner_table_width: float = 0.55
    inner_table_height: float = 0.3

    outer_table_color: str = 'SaddleBrown'
    outer_table_width: float = 0.6
    outer_table_height: float = 0.35

    button_ring_width: float = 0.5
    button_ring_height: float = 0.25
    button_angle: float = pi / 24
    button_color: str = 'White'
    button_diameter: float = 0.035
    button_text_color: str = 'Black'
    button_text_font: str = 'bold {}px sans-serif'
    button_text_height: float = 0.025
    button_text: str = 'B'

    bet_ring_width: float = 0.425
    bet_ring_height: float = 0.175
    bet_angle: float = 0
    bet_box_color: str = 'Black'
    bet_box_height: float = 0.025
    bet_text: str = '{}'
    bet_text_color: str = 'White'
    bet_text_font: str = 'bold {}px sans-serif'
    bet_text_height: float = 0.02

    board_y: float = 0.05
    board_width: float = 0.3
    board_height: float = 0.025
    board_radius: float = 0.003
    board_color: str = 'Black'
    board_text: str = 'Pot: {}'
    board_text_color: str = 'White'
    board_text_font: str = 'bold {}px sans-serif'
    board_text_height: float = 0.02

    board_card_margin: float = 0.0025
    board_card_padding_percentage: float = 0.1
    board_card_radius: float = 0.005
    board_card_color: str = 'White'
    board_card_text_font: str = 'bold {}px sans-serif'

    club_color: str = 'Green'
    diamond_color: str = 'Blue'
    heart_color: str = 'Red'
    spade_color: str = 'Black'
    unknown_color: str = 'White'

    seat_ring_width: float = 0.8
    seat_ring_height: float = 0.55

    name_y: float = 0
    name_width: float = 0.25
    name_height: float = 0.025
    name_radius: float = 0.003
    name_color: str = 'Black'
    name_text: str = '{}'
    name_text_color: str = 'White'
    name_text_font: str = 'bold {}px sans-serif'
    name_text_height: float = 0.02

    stack_y: float = 0.025
    stack_width: float = 0.25
    stack_height: float = 0.025
    stack_color: str = 'DarkBlue'
    stack_text: str = 'Stack: {}'
    stack_text_color: str = 'White'
    stack_text_font: str = 'bold {}px sans-serif'
    stack_text_height: float = 0.02

    acted_y: float = 0.05
    acted_width: float = 0.25
    acted_height: float = 0.025
    acted_radius: float = 0.003
    acted_color: str = 'DarkGray'
    acted_text: str = '{}'
    acted_text_color: str = 'Black'
    acted_text_font: str = 'bold {}px sans-serif'
    acted_text_height: float = 0.02

    hole_card_margin: float = 0.003
    hole_card_padding_percentage: float = 0.1
    hole_card_radius: float = 0.005
    hole_card_color: str = 'White'
    hole_card_text_font: str = 'bold {}px sans-serif'


@dataclass
class Data:
    _: KW_ONLY
    names: list[str | None]
    button: int | None
    bets: list[int | None]
    stacks: list[int | None]
    pots: list[int]
    hole: list[list[Card] | None]
    hole_statuses: list[bool]
    board: list[Card]
    board_count: int
    acted: tuple[int, str] | None
    actor: int | None
    timestamps: list[datetime] | None

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
                state = hand_history.create_state(())
                status = False
            else:
                status = True

            acted = None
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

            hole = p2s(map(list.copy, state.hole_cards))
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
                acted = p2s(operation.player_index), action

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
                hole=hole,
                hole_statuses=hole_statuses,
                board=board,
                board_count=board_count,
                acted=acted,
                actor=actor,
                timestamps=None,
            )
