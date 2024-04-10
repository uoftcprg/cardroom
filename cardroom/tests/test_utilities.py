from datetime import datetime
from math import inf
import builtins

from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils.module_loading import import_string

from cardroom.felt import Style
from cardroom.utilities import (
    DEFAULT_ADMIN,
    DEFAULT_AUTH,
    DEFAULT_DECIMAL_PLACES,
    DEFAULT_DIVMOD,
    DEFAULT_FELT,
    DEFAULT_PARSE_VALUE,
    DEFAULT_RAT_HOLING_STATUS,
    DEFAULT_ROOT_ROUTINGCONF,
    DEFAULT_STYLE,
    get_admin,
    get_auth,
    get_decimal_places,
    get_divmod,
    get_felt,
    get_parse_value,
    get_rat_holing_status,
    get_root_routingconf,
    get_style,
    serialize,
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
        self.assertEqual(get_parse_value()(str(8 / 3)), 3)

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
            CARDROOM_DECIMAL_PLACES=2,
            CARDROOM_AUTH=False,
            CARDROOM_ADMIN=False,
            CARDROOM_RAT_HOLING_STATUS=False,
            CARDROOM_FELT=False,
            CARDROOM_STYLE=Style(background_color=''),
            ROOT_ROUTINGCONF=''
    )
    def test_non_defaults_1(self) -> None:
        self.assertEqual(get_divmod(), builtins.divmod)
        self.assertEqual(get_parse_value(), int)
        self.assertEqual(get_decimal_places(), 2)
        self.assertFalse(get_auth())
        self.assertFalse(get_admin())
        self.assertFalse(get_rat_holing_status())
        self.assertFalse(get_felt())
        self.assertEqual(get_style(), Style(background_color=''))
        self.assertEqual(get_root_routingconf(), '')

        self.assertNotEqual(get_divmod(), import_string(DEFAULT_DIVMOD))
        self.assertNotEqual(
            get_parse_value(),
            import_string(DEFAULT_PARSE_VALUE),
        )
        self.assertNotEqual(get_decimal_places(), DEFAULT_DECIMAL_PLACES)
        self.assertNotEqual(get_auth(), DEFAULT_AUTH)
        self.assertNotEqual(get_admin(), DEFAULT_ADMIN)
        self.assertNotEqual(get_rat_holing_status(), DEFAULT_RAT_HOLING_STATUS)
        self.assertNotEqual(get_felt(), DEFAULT_FELT)
        self.assertNotEqual(get_style(), DEFAULT_STYLE)
        self.assertNotEqual(get_root_routingconf(), DEFAULT_ROOT_ROUTINGCONF)

        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE
        del settings.CARDROOM_DECIMAL_PLACES
        del settings.CARDROOM_AUTH
        del settings.CARDROOM_ADMIN
        del settings.CARDROOM_RAT_HOLING_STATUS
        del settings.CARDROOM_FELT
        del settings.CARDROOM_STYLE
        del settings.ROOT_ROUTINGCONF

        self.assertEqual(get_divmod(), import_string(DEFAULT_DIVMOD))
        self.assertEqual(get_parse_value(), import_string(DEFAULT_PARSE_VALUE))
        self.assertEqual(get_decimal_places(), DEFAULT_DECIMAL_PLACES)
        self.assertEqual(get_auth(), DEFAULT_AUTH)
        self.assertEqual(get_admin(), DEFAULT_ADMIN)
        self.assertEqual(get_rat_holing_status(), DEFAULT_RAT_HOLING_STATUS)
        self.assertEqual(get_felt(), DEFAULT_FELT)
        self.assertEqual(get_style(), DEFAULT_STYLE)
        self.assertEqual(get_root_routingconf(), DEFAULT_ROOT_ROUTINGCONF)

    @override_settings()
    def test_defaults(self) -> None:
        self.assertEqual(get_divmod(), import_string(DEFAULT_DIVMOD))
        self.assertEqual(get_parse_value(), import_string(DEFAULT_PARSE_VALUE))
        self.assertEqual(get_decimal_places(), DEFAULT_DECIMAL_PLACES)
        self.assertEqual(get_auth(), DEFAULT_AUTH)
        self.assertEqual(get_admin(), DEFAULT_ADMIN)
        self.assertEqual(get_rat_holing_status(), DEFAULT_RAT_HOLING_STATUS)
        self.assertEqual(get_felt(), DEFAULT_FELT)
        self.assertEqual(get_style(), DEFAULT_STYLE)
        self.assertEqual(get_root_routingconf(), DEFAULT_ROOT_ROUTINGCONF)

        del settings.CARDROOM_DIVMOD
        del settings.CARDROOM_PARSE_VALUE
        del settings.CARDROOM_DECIMAL_PLACES
        del settings.CARDROOM_AUTH
        del settings.CARDROOM_ADMIN
        del settings.CARDROOM_RAT_HOLING_STATUS
        del settings.CARDROOM_FELT
        del settings.CARDROOM_STYLE
        del settings.ROOT_ROUTINGCONF

        self.assertEqual(get_divmod(), import_string(DEFAULT_DIVMOD))
        self.assertEqual(get_parse_value(), import_string(DEFAULT_PARSE_VALUE))
        self.assertEqual(get_decimal_places(), DEFAULT_DECIMAL_PLACES)
        self.assertEqual(get_auth(), DEFAULT_AUTH)
        self.assertEqual(get_admin(), DEFAULT_ADMIN)
        self.assertEqual(get_rat_holing_status(), DEFAULT_RAT_HOLING_STATUS)
        self.assertEqual(get_felt(), DEFAULT_FELT)
        self.assertEqual(get_style(), DEFAULT_STYLE)
        self.assertEqual(get_root_routingconf(), DEFAULT_ROOT_ROUTINGCONF)

    def test_serialize(self) -> None:
        dt = datetime.now()

        self.assertEqual(
            serialize({3: [1, {1}, dt], dt: False}),
            {3: [1, [1], dt.isoformat()], dt.isoformat(): False},
        )
