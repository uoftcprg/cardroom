from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, is_dataclass
from math import inf, floor, pi
from typing import Any, cast
from zoneinfo import ZoneInfo
import math

from django.conf import settings
from django.utils.module_loading import import_string
import pokerkit

from cardroom.felt import Configuration

DEFAULT_DIVMOD: str = 'cardroom.utilities.divmod'
DEFAULT_PARSE_VALUE: str = 'cardroom.utilities.parse_value'
DEFAULT_DECIMAL_PLACES: int | float = inf
DEFAULT_AUTH: bool = False
DEFAULT_ADMIN: bool = False
DEFAULT_FELT: bool = False
DEFAULT_CONFIGURATION: Configuration = Configuration(
    background_color='gray',
    table_border_color='saddlebrown',
    table_felt_color='seagreen',
    table_x=0,
    table_y=0,
    table_outer_width=0.6,
    table_outer_height=0.35,
    table_inner_width=0.55,
    table_inner_height=0.3,
    button_color='white',
    button_angle=pi / 24,
    button_ring_width=0.5,
    button_ring_height=0.25,
    button_diameter=0.035,
    button_text_color='black',
    button_text_style='bold',
    button_text_font='sans',
    button_text_size=0.025,
    button_text='B',
    board_x=0,
    board_y=-0.05,
    board_width=0.3,
    board_height=0.025,
    board_radius=0.0125,
    board_color='black',
    board_pot_text='Pot: ',
    board_pot_text_color='white',
    board_pot_text_style='bold',
    board_pot_text_font='sans',
    board_pot_text_size=0.02,
    board_card_margin=0.0025,
    board_card_height=0.06,
    board_card_radius=0.005,
    board_card_color='white',
    board_card_text_style='bold',
    board_card_text_font='sans',
    board_card_text_size=0.025,
    bet_ring_width=0.425,
    bet_ring_height=0.175,
    bet_angle=0,
    bet_box_color='black',
    bet_box_x_padding=0.025,
    bet_box_height=0.025,
    bet_box_radius=0.0125,
    bet_text_style='bold',
    bet_text_color='white',
    bet_text_font='sans',
    bet_text_size=0.02,
    seat_ring_width=0.8,
    seat_ring_height=0.55,
    seat_angle=0,
    hole_x=0,
    hole_y=0,
    hole_width=0.225,
    hole_height=0.03,
    hole_radius=0.005,
    hole_color='black',
    hole_card_margin=0.003,
    hole_card_height=0.05,
    hole_card_radius=0.004,
    hole_card_color='white',
    hole_card_text_style='bold',
    hole_card_text_font='sans',
    hole_card_text_size=0.025,
    name_x=0,
    name_y=0,
    name_box_width=0.225,
    name_box_height=0.03,
    name_box_radius=0,
    name_box_color='darkblue',
    name_text_style='bold',
    name_text_color='white',
    name_text_font='sans',
    name_text_size=0.02,
    stack_x=0,
    stack_y=-0.03,
    stack_box_width=0.225,
    stack_box_height=0.03,
    stack_box_radius=0,
    stack_box_color='black',
    stack_text_style='bold',
    stack_text_color='white',
    stack_text_font='sans',
    stack_text_size=0.02,
    previous_action_x=0,
    previous_action_y=-0.06,
    previous_action_box_width=0.225,
    previous_action_box_height=0.03,
    previous_action_box_radius=0,
    previous_action_box_color='darkgray',
    previous_action_text_style='bold',
    previous_action_text_color='black',
    previous_action_text_font='sans',
    previous_action_text_size=0.02,
    club_color='green',
    diamond_color='blue',
    heart_color='red',
    spade_color='black',
    unknown_color='white',
    shifter_timeout=0.25,
    watchdog_timeout=1,
    frame_rate=1000,
)
DEFAULT_ROOT_ROUTINGCONF: str = 'cardroom.routing'
DEFAULT_GAMEMASTER_TIMEOUT: float = 1
_divmod = divmod


def divmod(dividend: int, divisor: int) -> tuple[int, int]:
    quotient: int | float
    remainder: int | float

    match get_decimal_places():
        case 0:
            quotient, remainder = _divmod(int(dividend), int(divisor))
        case math.inf:
            quotient, remainder = dividend / divisor, 0
        case decimal_places:
            assert isinstance(decimal_places, int)

            quotient = (
                floor(dividend / divisor * 10 ** decimal_places)
                / (10 ** decimal_places)
            )
            remainder = dividend - quotient * divisor

    return cast(tuple[int, int], (quotient, remainder))


def parse_value(raw_value: str) -> int:
    value = pokerkit.parse_value(raw_value)

    match get_decimal_places():
        case 0:
            value = int(value)
        case math.inf:
            pass
        case decimal_places:
            assert isinstance(decimal_places, int)

            value = round(value, decimal_places)

    return value


def get_tzinfo() -> ZoneInfo:
    return ZoneInfo(getattr(settings, 'TIME_ZONE', 'UTC'))


def get_divmod() -> Callable[[int, int], tuple[int, int]]:
    return import_string(getattr(settings, 'CARDROOM_DIVMOD', DEFAULT_DIVMOD))


def get_parse_value() -> Callable[[str], int]:
    return import_string(
        getattr(settings, 'CARDROOM_PARSE_VALUE', DEFAULT_PARSE_VALUE),
    )


def get_decimal_places() -> int | float:
    return getattr(settings, 'CARDROOM_DECIMAL_PLACES', DEFAULT_DECIMAL_PLACES)


def get_auth() -> bool:
    return getattr(settings, 'CARDROOM_AUTH', DEFAULT_AUTH)


def get_admin() -> bool:
    return getattr(settings, 'CARDROOM_ADMIN', DEFAULT_ADMIN)


def get_felt() -> bool:
    return getattr(settings, 'CARDROOM_FELT', DEFAULT_FELT)


def get_configuration() -> Configuration:
    return getattr(settings, 'CARDROOM_CONFIGURATION', DEFAULT_CONFIGURATION)


def get_root_routingconf() -> Any:
    return getattr(settings, 'ROOT_ROUTINGCONF', DEFAULT_ROOT_ROUTINGCONF)


def get_gamemaster_timeout() -> Any:
    return getattr(settings, 'GAMEMASTER_TIMEOUT', DEFAULT_GAMEMASTER_TIMEOUT)


def serialize(obj: Any) -> Any:
    if obj is None or isinstance(obj, bytes | str | int | float | bool):
        return obj
    elif is_dataclass(obj):
        return serialize(asdict(obj))
    elif isinstance(obj, Mapping):
        return dict(zip(serialize(obj.keys()), serialize(obj.values())))
    elif isinstance(obj, Iterable):
        return list(map(serialize, obj))
    else:
        raise AssertionError
