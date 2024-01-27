from pickle import dumps
from textwrap import dedent

from django.test import TestCase
from pokerkit import Automation, NoLimitShortDeckHoldem, NoLimitTexasHoldem
import pokerkit

from cardroom.models import Poker, Table, HandHistory
from cardroom.utilities import get_divmod
import cardroom.table as table


class PickleTestCaseMixin(TestCase):
    def assertPickleEqual(self, o1: object, o2: object) -> None:
        self.assertEqual(dumps(o1), dumps(o2))


class PokerTestCase(PickleTestCaseMixin, TestCase):
    def test_load(self) -> None:
        self.assertPickleEqual(
            Poker.objects.create(
                variant='NT',
                raw_antes={1: 3},
                raw_blinds_or_straddles=[1, 2],
                min_bet=2,
            ).load(),
            NoLimitTexasHoldem(
                Poker.automations,
                False,
                {1: 3},
                [1, 2],
                2,
                get_divmod(),
            ),
        )
        self.assertPickleEqual(
            Poker.objects.create(
                variant='NT',
                raw_antes=[0, 3],
                raw_blinds_or_straddles=[1, 2],
                min_bet=2,
            ).load(),
            NoLimitTexasHoldem(
                Poker.automations,
                False,
                [0, 3],
                [1, 2],
                2,
                get_divmod(),
            ),
        )
        self.assertPickleEqual(
            Poker.objects.create(
                variant='NT',
                ante_trimming_status=True,
                raw_antes=0,
                raw_blinds_or_straddles=[1, 2],
                min_bet=2,
            ).load(),
            NoLimitTexasHoldem(
                Poker.automations,
                True,
                0,
                [1, 2],
                2,
                get_divmod(),
            ),
        )
        self.assertPickleEqual(
            Poker.objects.create(
                variant='NS',
                ante_trimming_status=True,
                raw_antes=2,
                raw_blinds_or_straddles={-1: 2},
                min_bet=2,
            ).load(),
            NoLimitShortDeckHoldem(
                Poker.automations,
                True,
                2,
                {-1: 2},
                2,
                get_divmod(),
            ),
        )


class TableTestCase(PickleTestCaseMixin, TestCase):
    def test_load(self) -> None:
        game = Poker.objects.create(
            variant='NT',
            raw_antes={1: 3},
            raw_blinds_or_straddles=[1, 2],
            min_bet=2,
        )

        self.assertPickleEqual(
            Table.objects.create(
                game=game,
                seat_count=6,
                min_starting_stack=80,
                max_starting_stack=200,
            ).load(),
            table.Table(
                NoLimitTexasHoldem(
                    Poker.automations,
                    False,
                    {1: 3},
                    [1, 2],
                    2,
                    get_divmod(),
                ),
                6,
                80,
                200,
            ),
        )


class HandHistoryTestCase(TestCase):
    def test_dump_and_load(self) -> None:
        s = dedent(
            '''\
            # An example badugi hand from Wikipedia.
            # Link: https://en.wikipedia.org/wiki/Badugi

            variant = "FB"
            ante_trimming_status = true
            antes = [0, 0, 0, 0]
            blinds_or_straddles = [1, 2, 0, 0]
            small_bet = 2
            big_bet = 4
            starting_stacks = [200, 200, 200, 200]
            actions = [
              # Pre-draw

              "d dh p1 ????????",  # Bob
              "d dh p2 ????????",  # Carol
              "d dh p3 ????????",  # Ted
              "d dh p4 ????????",  # Alice

              "p3 f",  # Ted
              "p4 cc",  # Alice
              "p1 cc",  # Bob
              "p2 cc",  # Carol

              # First draw

              "p1 sd ????",  # Bob
              "p2 sd ????",  # Carol
              "p4 sd ??",  # Alice
              "d dh p1 ????",  # Bob
              "d dh p2 ????",  # Carol
              "d dh p4 ??",  # Alice

              "p1 cc",  # Bob
              "p2 cbr 2",  # Carol
              "p4 cc",  # Alice
              "p1 cc",  # Bob

              # Second draw

              "p1 sd ??",  # Bob
              "p2 sd",  # Carol
              "p4 sd ??",  # Alice
              "d dh p1 ??",  # Bob
              "d dh p4 ??",  # Alice

              "p1 cc",  # Bob
              "p2 cbr 4",  # Carol
              "p4 cbr 8",  # Alice
              "p1 f",  # Bob
              "p2 cc",  # Bob

              # Third draw

              "p2 sd ??",  # Carol
              "p4 sd",  # Alice
              "d dh p2 ??",  # Carol

              "p2 cc",  # Carol
              "p4 cbr 4",  # Alice
              "p2 cc",  # Carol

              # Showdown

              "p4 sm 2s4c6d9h",  # Alice
              "p2 sm 3s5d7c8h",  # Carol
            ]
            author = "Juho Kim"
            players = ["Bob", "Carol", "Ted", "Alice"]
            '''
        )
        pkhh0 = pokerkit.HandHistory.loads(
            s,
            automations=(Automation.CARD_BURNING,),
        )
        hh0 = HandHistory.dump(pkhh0)
        hh0.save()
        hh1 = HandHistory.objects.first()

        assert hh1 is not None

        pkhh1 = hh1.load()

        self.assertEqual(pkhh0, pkhh1)
