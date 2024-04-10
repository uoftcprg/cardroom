from dataclasses import dataclass, KW_ONLY
from math import pi
from typing import TypeVar

_T = TypeVar('_T')


@dataclass(frozen=True)
class Style:
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
