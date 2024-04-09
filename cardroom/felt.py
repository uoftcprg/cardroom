from dataclasses import dataclass, KW_ONLY
from typing import TypeVar

_T = TypeVar('_T')


@dataclass(frozen=True)
class Style:
    _: KW_ONLY

    background_color: str

    table_border_color: str
    table_felt_color: str
    table_x: float
    table_y: float
    table_outer_width: float
    table_outer_height: float
    table_inner_width: float
    table_inner_height: float

    button_color: str
    button_angle: float
    button_ring_width: float
    button_ring_height: float
    button_diameter: float
    button_text_color: str
    button_text_style: str
    button_text_font: str
    button_text_size: float
    button_text: str

    board_x: float
    board_y: float
    board_width: float
    board_height: float
    board_radius: float
    board_color: str
    board_pot_text: str
    board_pot_text_color: str
    board_pot_text_style: str
    board_pot_text_font: str
    board_pot_text_size: float
    board_card_margin: float
    board_card_height: float
    board_card_radius: float
    board_card_color: str
    board_card_text_style: str
    board_card_text_font: str
    board_card_text_size: float

    bet_ring_width: float
    bet_ring_height: float
    bet_angle: float
    bet_box_color: str
    bet_box_x_padding: float
    bet_box_height: float
    bet_box_radius: float
    bet_text_style: str
    bet_text_color: str
    bet_text_font: str
    bet_text_size: float

    seat_ring_width: float
    seat_ring_height: float
    seat_angle: float

    hole_x: float
    hole_y: float
    hole_width: float
    hole_height: float
    hole_radius: float
    hole_color: str
    hole_card_margin: float
    hole_card_height: float
    hole_card_radius: float
    hole_card_color: str
    hole_card_text_style: str
    hole_card_text_font: str
    hole_card_text_size: float

    name_x: float
    name_y: float
    name_box_width: float
    name_box_height: float
    name_box_radius: float
    name_box_color: str
    name_text_style: str
    name_text_color: str
    name_text_font: str
    name_text_size: float

    stack_x: float
    stack_y: float
    stack_box_width: float
    stack_box_height: float
    stack_box_radius: float
    stack_box_color: str
    stack_text_style: str
    stack_text_color: str
    stack_text_font: str
    stack_text_size: float

    previous_action_x: float
    previous_action_y: float
    previous_action_box_width: float
    previous_action_box_height: float
    previous_action_box_radius: float
    previous_action_box_color: str
    previous_action_text_style: str
    previous_action_text_color: str
    previous_action_text_font: str
    previous_action_text_size: float

    club_color: str
    diamond_color: str
    heart_color: str
    spade_color: str
    unknown_color: str

    shifter_timeout: float
    watchdog_timeout: float

    frame_rate: float
