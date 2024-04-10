from collections.abc import Callable, Iterable, Mapping
from dataclasses import asdict, is_dataclass
from datetime import datetime
from math import floor
from typing import Any, cast
from zoneinfo import ZoneInfo
import builtins
import math

from django.conf import settings
from django.utils.module_loading import import_string
import pokerkit

from cardroom.felt import Style

DEFAULT_DIVMOD: str = 'cardroom.utilities.divmod'
DEFAULT_PARSE_VALUE: str = 'cardroom.utilities.parse_value'
DEFAULT_DECIMAL_PLACES: int = 0
DEFAULT_AUTH: bool = True
DEFAULT_ADMIN: bool = True
DEFAULT_RAT_HOLING_STATUS: bool = True
DEFAULT_FELT: bool = True
DEFAULT_STYLE: Style = Style()
DEFAULT_ROOT_ROUTINGCONF: str = 'cardroom.routings'


def divmod(dividend: int, divisor: int) -> tuple[int, int]:
    quotient: float
    remainder: float

    match get_decimal_places():
        case 0:
            quotient, remainder = builtins.divmod(dividend, divisor)
        case math.inf:
            quotient, remainder = dividend / divisor, 0
        case decimal_places:
            assert isinstance(decimal_places, int)

            quotient = (
                floor(dividend / divisor * 10 ** decimal_places)
                / (10 ** decimal_places)
            )
            remainder = dividend - divisor * quotient

    return cast(tuple[int, int], (quotient, remainder))


def parse_value(raw_value: str) -> int:
    value = pokerkit.parse_value(raw_value)

    match get_decimal_places():
        case 0:
            value = round(value)
        case math.inf:
            pass
        case decimal_places:
            assert isinstance(decimal_places, int)

            value = round(value, decimal_places)

    return value


def get_tzinfo() -> ZoneInfo:
    return ZoneInfo(getattr(settings, 'TIME_ZONE', 'UTC'))


def get_divmod() -> Callable[[int, int], tuple[int, int]]:
    return cast(
        Callable[[int, int], tuple[int, int]],
        import_string(getattr(settings, 'CARDROOM_DIVMOD', DEFAULT_DIVMOD)),
    )


def get_parse_value() -> Callable[[str], int]:
    return cast(
        Callable[[str], int],
        import_string(
            getattr(settings, 'CARDROOM_PARSE_VALUE', DEFAULT_PARSE_VALUE),
        ),
    )


def get_decimal_places() -> int:
    return getattr(settings, 'CARDROOM_DECIMAL_PLACES', DEFAULT_DECIMAL_PLACES)


def get_auth() -> bool:
    return getattr(settings, 'CARDROOM_AUTH', DEFAULT_AUTH)


def get_admin() -> bool:
    return getattr(settings, 'CARDROOM_ADMIN', DEFAULT_ADMIN)


def get_rat_holing_status() -> bool:
    return getattr(
        settings,
        'CARDROOM_RAT_HOLING_STATUS',
        DEFAULT_RAT_HOLING_STATUS,
    )


def get_felt() -> bool:
    return getattr(settings, 'CARDROOM_FELT', DEFAULT_FELT)


def get_style() -> Style:
    return getattr(settings, 'CARDROOM_STYLE', DEFAULT_STYLE)


def get_root_routingconf() -> str:
    return getattr(settings, 'ROOT_ROUTINGCONF', DEFAULT_ROOT_ROUTINGCONF)


def serialize(obj: Any) -> Any:
    if obj is None or isinstance(obj, bytes | str | int | float | bool):
        return obj
    elif is_dataclass(obj):
        return serialize(asdict(obj))
    elif isinstance(obj, Mapping):
        return dict(zip(serialize(obj.keys()), serialize(obj.values())))
    elif isinstance(obj, Iterable):
        return list(map(serialize, obj))
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise AssertionError
