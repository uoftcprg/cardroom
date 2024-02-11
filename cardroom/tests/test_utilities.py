from math import inf

from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

_divmod = divmod

from cardroom.utilities import (  # noqa: E402
    divmod,
    get_admin,
    get_decimal_places,
    get_divmod,
    get_felt,
    get_parse_value,
    parse_value,
)


class UtilitiesTestCase(SimpleTestCase):
    @override_settings(CARDROOM_DECIMAL_PLACES=0)
    def test_zero_decimal_places(self) -> None:
        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE

        self.assertEqual(get_divmod()(3, 2), (1, 1))
        self.assertEqual(get_divmod()(8, 3), (2, 2))
        self.assertEqual(get_parse_value()('0'), 0)
        self.assertEqual(get_parse_value()('1.25'), 1)
        self.assertEqual(get_parse_value()(str(8 / 3)), 2)

    @override_settings(CARDROOM_DECIMAL_PLACES=2)
    def test_two_decimal_places(self) -> None:
        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE

        self.assertEqual(get_divmod()(3, 2), (1.5, 0))
        self.assertEqual(get_divmod()(8, 3)[0], 2.66)
        self.assertAlmostEqual(get_divmod()(8, 3)[1], 0.02)
        self.assertEqual(
            get_divmod()(3.0, 2.0),  # type: ignore[arg-type]
            (1.5, 0.0),
        )
        self.assertEqual(
            get_divmod()(8.0, 3.0)[0],  # type: ignore[arg-type]
            2.66,
        )
        self.assertAlmostEqual(  # type: ignore[misc]
            get_divmod()(8.0, 3.0)[1],  # type: ignore[arg-type]
            0.02,
        )
        self.assertEqual(get_parse_value()('0'), 0.0)
        self.assertEqual(get_parse_value()('1.25'), 1.25)
        self.assertEqual(get_parse_value()(str(8 / 3)), 2.67)

    @override_settings(CARDROOM_DECIMAL_PLACES=inf)
    def test_inf_decimal_places(self) -> None:
        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE

        self.assertEqual(get_divmod()(3, 2), (1.5, 0))
        self.assertEqual(get_divmod()(8, 3), (8 / 3, 0))
        self.assertEqual(
            get_divmod()(3.0, 2.0),  # type: ignore[arg-type]
            (1.5, 0.0),
        )
        self.assertEqual(
            get_divmod()(8.0, 3.0),  # type: ignore[arg-type]
            (8 / 3, 0.0),
        )
        self.assertEqual(get_parse_value()('0'), 0)
        self.assertEqual(get_parse_value()('1.25'), 1.25)
        self.assertEqual(get_parse_value()(str(8 / 3)), 8 / 3)

    @override_settings(
            CARDROOM_DIVMOD='builtins.divmod',
            CARDROOM_PARSE_VALUE='builtins.int',
            CARDROOM_DECIMAL_PLACES=0,
            CARDROOM_ADMIN=True,
            CARDROOM_FELT=True,
    )
    def test_non_defaults_0(self) -> None:
        self.assertIs(get_divmod(), _divmod)
        self.assertIs(get_parse_value(), int)
        self.assertEqual(get_decimal_places(), 0)
        self.assertTrue(get_admin())
        self.assertTrue(get_felt())

    @override_settings(
            CARDROOM_DIVMOD='cardroom.utilities.divmod',
            CARDROOM_PARSE_VALUE='cardroom.utilities.parse_value',
            CARDROOM_DECIMAL_PLACES=2,
            CARDROOM_ADMIN=False,
            CARDROOM_FELT=False,
    )
    def test_non_defaults_1(self) -> None:
        self.assertIs(get_divmod(), divmod)
        self.assertIs(get_parse_value(), parse_value)
        self.assertEqual(get_decimal_places(), 2)
        self.assertFalse(get_admin())
        self.assertFalse(get_felt())

    @override_settings()
    def test_defaults(self) -> None:
        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE
        del settings.CARDROOM_DECIMAL_PLACES
        del settings.CARDROOM_ADMIN
        del settings.CARDROOM_FELT

        self.assertIs(get_divmod(), divmod)
        self.assertIs(get_parse_value(), parse_value)
        self.assertEqual(get_decimal_places(), inf)
        self.assertFalse(get_admin())
        self.assertFalse(get_felt())
