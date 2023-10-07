from collections.abc import Callable
from threading import Thread
from time import sleep
from typing import Any, ClassVar
from unittest import main, TestCase
from unittest.mock import MagicMock
from warnings import resetwarnings, simplefilter

from pokerkit import (
    BettingStructure,
    Deck,
    Hand,
    NoLimitDeuceToSevenLowballSingleDraw,
    Opening,
    Operation,
    StandardHighHand,
    StandardLowHand,
    Street,
    ValuesLike,
)

from cardroom.table import Table


class TableTestCase(TestCase):
    SEAT_COUNT: ClassVar[int] = 6
    BUTTON_STATUS_A: ClassVar[bool] = True
    DECK_A: ClassVar[Deck] = Deck.STANDARD
    HAND_TYPES_A: ClassVar[tuple[type[Hand], ...]] = (StandardHighHand,)
    STREETS_A: ClassVar[tuple[Street, ...]] = (
        Street(
            False,
            (False,) * 2,
            0,
            False,
            Opening.POSITION,
            1,
            None,
        ),
        Street(
            True,
            (),
            3,
            False,
            Opening.POSITION,
            1,
            None,
        ),
        Street(
            True,
            (),
            1,
            False,
            Opening.POSITION,
            1,
            None,
        ),
        Street(
            True,
            (),
            1,
            False,
            Opening.POSITION,
            1,
            None,
        ),
    )
    BETTING_STRUCTURE_A: ClassVar[BettingStructure] = BettingStructure.NO_LIMIT
    ANTE_TRIMMING_STATUS_A: ClassVar[bool] = True
    RAW_ANTES_A: ClassVar[ValuesLike] = None
    RAW_BLINDS_OR_STRADDLES_A: ClassVar[ValuesLike] = 1, 2
    BRING_IN_A: ClassVar[int] = 0
    BUTTON_STATUS_B: ClassVar[bool] = False
    DECK_B: ClassVar[Deck] = Deck.STANDARD
    HAND_TYPES_B: ClassVar[tuple[type[Hand], ...]] = (StandardHighHand,)
    STREETS_B: ClassVar[tuple[Street, ...]] = (
        Street(
            False,
            (False, False, True),
            0,
            False,
            Opening.LOW_CARD,
            2,
            4,
        ),
        Street(
            True, (True,),
            0,
            False,
            Opening.HIGH_HAND,
            2,
            4,
        ),
        Street(
            True,
            (True,),
            0,
            False,
            Opening.HIGH_HAND,
            4,
            4,
        ),
        Street(
            True,
            (True,),
            0,
            False,
            Opening.HIGH_HAND,
            4,
            4,
        ),
        Street(
            True,
            (False,),
            0,
            False,
            Opening.HIGH_HAND,
            4,
            4,
        ),
    )
    BETTING_STRUCTURE_B: ClassVar[BettingStructure] = (
        BettingStructure.FIXED_LIMIT
    )
    ANTE_TRIMMING_STATUS_B: ClassVar[bool] = True
    RAW_ANTES_B: ClassVar[ValuesLike] = 1
    RAW_BLINDS_OR_STRADDLES_B: ClassVar[ValuesLike] = None
    BRING_IN_B: ClassVar[int] = 1
    BUTTON_STATUS_C: ClassVar[bool] = True
    DECK_C: ClassVar[Deck] = Deck.STANDARD
    HAND_TYPES_C: ClassVar[tuple[type[Hand], ...]] = (StandardLowHand,)
    STREETS_C: ClassVar[tuple[Street, ...]] = (
        Street(
            False,
            (False,) * 5,
            0,
            False,
            Opening.POSITION,
            2,
            None,
        ),
        Street(
            True,
            (),
            0,
            True,
            Opening.POSITION,
            2,
            None,
        ),
    )
    BETTING_STRUCTURE_C: ClassVar[BettingStructure] = BettingStructure.NO_LIMIT
    ANTE_TRIMMING_STATUS_C: ClassVar[bool] = False
    RAW_ANTES_C: ClassVar[ValuesLike] = {1: 2}
    RAW_BLINDS_OR_STRADDLES_C: ClassVar[ValuesLike] = 1, 2
    BRING_IN_C: ClassVar[int] = 0
    BUY_IN_RANGE: ClassVar[range] = range(80, 201)
    TIMEBANK: ClassVar[float] = 30
    TIMEBANK_INCREMENT: ClassVar[float] = 1
    PLAY_TIMEOUT: ClassVar[float] = 1
    IDLE_TIMEOUT: ClassVar[float] = 100
    ANTE_POSTING_TIMEOUT: ClassVar[float] = 0.05
    BET_COLLECTION_TIMEOUT: ClassVar[float] = 0.1
    BLIND_OR_STRADDLE_POSTING_TIMEOUT: ClassVar[float] = 0.05
    CARD_BURNING_TIMEOUT: ClassVar[float] = 0.1
    HOLE_DEALING_TIMEOUT: ClassVar[float] = 0.1
    BOARD_DEALING_TIMEOUT: ClassVar[float] = 0.1
    STANDING_PAT_TIMEOUT: ClassVar[float] = 10
    FOLDING_TIMEOUT: ClassVar[float] = 10
    CHECKING_TIMEOUT: ClassVar[float] = 10
    BRING_IN_POSTING_TIMEOUT: ClassVar[float] = 10
    HOLE_CARDS_SHOWING_OR_MUCKING_TIMEOUT: ClassVar[float] = 3
    HAND_KILLING_TIMEOUT: ClassVar[float] = 0.5
    CHIPS_PUSHING_TIMEOUT: ClassVar[float] = 0.5
    CHIPS_PULLING_TIMEOUT: ClassVar[float] = 0.5
    SKIP_TIMEOUT: ClassVar[float] = 1
    MIN_SLEEP_TIMEOUT: ClassVar[float] = 1
    SLEEP_TIMEOUT_MULTIPLIER: ClassVar[float] = 10
    EPOCH_TIMEOUT: ClassVar[float] = 60

    @classmethod
    def setUpClass(cls) -> None:
        simplefilter('ignore')

    @classmethod
    def tearDownClass(cls) -> None:
        resetwarnings()

    @classmethod
    def create_table_a(
            cls,
            callback: Callable[[Table, Operation | None], Any],
    ) -> Table:
        return Table(
            cls.SEAT_COUNT,
            cls.BUTTON_STATUS_A,
            cls.DECK_A,
            cls.HAND_TYPES_A,
            cls.STREETS_A,
            cls.BETTING_STRUCTURE_A,
            cls.ANTE_TRIMMING_STATUS_A,
            cls.RAW_ANTES_A,
            cls.RAW_BLINDS_OR_STRADDLES_A,
            cls.BRING_IN_A,
            cls.BUY_IN_RANGE,
            cls.TIMEBANK,
            cls.TIMEBANK_INCREMENT,
            cls.PLAY_TIMEOUT,
            cls.IDLE_TIMEOUT,
            cls.ANTE_POSTING_TIMEOUT,
            cls.BET_COLLECTION_TIMEOUT,
            cls.BLIND_OR_STRADDLE_POSTING_TIMEOUT,
            cls.CARD_BURNING_TIMEOUT,
            cls.HOLE_DEALING_TIMEOUT,
            cls.BOARD_DEALING_TIMEOUT,
            cls.STANDING_PAT_TIMEOUT,
            cls.FOLDING_TIMEOUT,
            cls.CHECKING_TIMEOUT,
            cls.BRING_IN_POSTING_TIMEOUT,
            cls.HOLE_CARDS_SHOWING_OR_MUCKING_TIMEOUT,
            cls.HAND_KILLING_TIMEOUT,
            cls.CHIPS_PUSHING_TIMEOUT,
            cls.CHIPS_PULLING_TIMEOUT,
            cls.SKIP_TIMEOUT,
            callback,
        )

    @classmethod
    def create_table_b(
            cls,
            callback: Callable[[Table, Operation | None], Any],
    ) -> Table:
        return Table(
            cls.SEAT_COUNT,
            cls.BUTTON_STATUS_B,
            cls.DECK_B,
            cls.HAND_TYPES_B,
            cls.STREETS_B,
            cls.BETTING_STRUCTURE_B,
            cls.ANTE_TRIMMING_STATUS_B,
            cls.RAW_ANTES_B,
            cls.RAW_BLINDS_OR_STRADDLES_B,
            cls.BRING_IN_B,
            cls.BUY_IN_RANGE,
            cls.TIMEBANK,
            cls.TIMEBANK_INCREMENT,
            cls.PLAY_TIMEOUT,
            cls.IDLE_TIMEOUT,
            cls.ANTE_POSTING_TIMEOUT,
            cls.BET_COLLECTION_TIMEOUT,
            cls.BLIND_OR_STRADDLE_POSTING_TIMEOUT,
            cls.CARD_BURNING_TIMEOUT,
            cls.HOLE_DEALING_TIMEOUT,
            cls.BOARD_DEALING_TIMEOUT,
            cls.STANDING_PAT_TIMEOUT,
            cls.FOLDING_TIMEOUT,
            cls.CHECKING_TIMEOUT,
            cls.BRING_IN_POSTING_TIMEOUT,
            cls.HOLE_CARDS_SHOWING_OR_MUCKING_TIMEOUT,
            cls.HAND_KILLING_TIMEOUT,
            cls.CHIPS_PUSHING_TIMEOUT,
            cls.CHIPS_PULLING_TIMEOUT,
            cls.SKIP_TIMEOUT,
            callback,
        )

    @classmethod
    def create_table_c(
            cls,
            callback: Callable[[Table, Operation | None], Any],
    ) -> Table:
        return Table(
            cls.SEAT_COUNT,
            cls.BUTTON_STATUS_C,
            cls.DECK_C,
            cls.HAND_TYPES_C,
            cls.STREETS_C,
            cls.BETTING_STRUCTURE_C,
            cls.ANTE_TRIMMING_STATUS_C,
            cls.RAW_ANTES_C,
            cls.RAW_BLINDS_OR_STRADDLES_C,
            cls.BRING_IN_C,
            cls.BUY_IN_RANGE,
            cls.TIMEBANK,
            cls.TIMEBANK_INCREMENT,
            cls.PLAY_TIMEOUT,
            cls.IDLE_TIMEOUT,
            cls.ANTE_POSTING_TIMEOUT,
            cls.BET_COLLECTION_TIMEOUT,
            cls.BLIND_OR_STRADDLE_POSTING_TIMEOUT,
            cls.CARD_BURNING_TIMEOUT,
            cls.HOLE_DEALING_TIMEOUT,
            cls.BOARD_DEALING_TIMEOUT,
            cls.STANDING_PAT_TIMEOUT,
            cls.FOLDING_TIMEOUT,
            cls.CHECKING_TIMEOUT,
            cls.BRING_IN_POSTING_TIMEOUT,
            cls.HOLE_CARDS_SHOWING_OR_MUCKING_TIMEOUT,
            cls.HAND_KILLING_TIMEOUT,
            cls.CHIPS_PUSHING_TIMEOUT,
            cls.CHIPS_PULLING_TIMEOUT,
            cls.SKIP_TIMEOUT,
            callback,
        )

    def test_seat_indices(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)

        self.assertEqual(table.seat_indices, range(self.SEAT_COUNT))

    def test_turn_index(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)

        self.assertIsNone(table.turn_index)

        table.state = NoLimitDeuceToSevenLowballSingleDraw.create_state(
            (),
            False,
            0,
            (1, 2),
            2,
            (200, 200),
            2,
        )

        while table.state.can_post_blind_or_straddle():
            self.assertIsNone(table.turn_index)
            table.state.post_blind_or_straddle()

        while table.state.can_deal_hole():
            self.assertIsNone(table.turn_index)
            table.state.deal_hole()

        self.assertEqual(table.turn_index, 1)
        table.state.check_or_call()
        self.assertEqual(table.turn_index, 0)
        table.state.check_or_call()
        self.assertEqual(table.turn_index, None)
        table.state.collect_bets()
        table.state.stand_pat_or_discard()
        self.assertEqual(table.turn_index, 1)
        table.state.stand_pat_or_discard()
        self.assertEqual(table.turn_index, None)
        table.state.burn_card()
        self.assertEqual(table.turn_index, 0)
        table.state.check_or_call()
        self.assertEqual(table.turn_index, 1)
        table.state.check_or_call()
        self.assertEqual(table.turn_index, 0)
        table.state.show_or_muck_hole_cards()
        self.assertEqual(table.turn_index, 1)
        table.state.show_or_muck_hole_cards()
        self.assertEqual(table.turn_index, None)

    def test_is_active(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)
        thread = Thread(target=table.run)

        thread.start()

        for i in table.seat_indices:
            self.assertFalse(table.is_active(i))

        table.connect('0', 0, self.BUY_IN_RANGE.start)
        sleep(self.MIN_SLEEP_TIMEOUT)

        for i in table.seat_indices:
            if i:
                self.assertFalse(table.is_active(i))
            else:
                self.assertTrue(table.is_active(i))

        table.deactivate('0')
        sleep(self.MIN_SLEEP_TIMEOUT)

        for i in table.seat_indices:
            self.assertFalse(table.is_active(i))

            if i:
                self.assertFalse(table.is_occupied(i))
            else:
                self.assertTrue(table.is_occupied(i))

        table.stop()
        thread.join()

    def test_get_seat_index(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)
        thread = Thread(target=table.run)

        thread.start()
        table.connect('0', 0, self.BUY_IN_RANGE.start)
        table.connect('1', 1, self.BUY_IN_RANGE.start)
        sleep(self.MIN_SLEEP_TIMEOUT)
        self.assertRaises(ValueError, table.get_seat_index, None)
        self.assertEqual(table.get_seat_index('0'), 0)
        self.assertEqual(table.get_seat_index('1'), 1)
        sleep(self.SLEEP_TIMEOUT_MULTIPLIER * self.PLAY_TIMEOUT)
        self.assertEqual(table.get_seat_index(0), 1)
        self.assertEqual(table.get_seat_index(1), 0)
        table.stop()
        thread.join()

    def test_connect_and_disconnect(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)
        thread = Thread(target=table.run)

        thread.start()
        table.connect('0', 0, self.BUY_IN_RANGE.start)
        table.connect('1', -1, self.BUY_IN_RANGE.start)
        table.connect('2', 2, -1)
        table.connect('3', 3, self.BUY_IN_RANGE.stop)
        table.connect('4', 4, self.BUY_IN_RANGE.start - 1)
        table.connect('5', 0, self.BUY_IN_RANGE.start)
        sleep(self.MIN_SLEEP_TIMEOUT)
        self.assertTrue(table.is_occupied(0))
        self.assertFalse(table.is_occupied(1))
        self.assertFalse(table.is_occupied(2))
        self.assertFalse(table.is_occupied(3))
        self.assertFalse(table.is_occupied(4))
        self.assertFalse(table.is_occupied(5))
        table.disconnect('0')
        sleep(self.MIN_SLEEP_TIMEOUT)
        self.assertFalse(table.is_occupied(0))
        table.stop()
        thread.join()

    def test_activate_and_deactivate(self) -> None:
        callback = MagicMock()
        table = self.create_table_a(callback)
        thread = Thread(target=table.run)

        thread.start()
        table.connect('0', 0, self.BUY_IN_RANGE.start)
        table.connect('1', 1, self.BUY_IN_RANGE.start)
        table.connect('2', 2, self.BUY_IN_RANGE.start)
        sleep(self.SLEEP_TIMEOUT_MULTIPLIER * self.PLAY_TIMEOUT)
        table.deactivate('0')
        table.deactivate('1')
        table.deactivate('2')
        sleep(self.EPOCH_TIMEOUT)
        table.activate('0')
        sleep(self.SLEEP_TIMEOUT_MULTIPLIER * self.PLAY_TIMEOUT)
        self.assertIsNone(table.state)
        self.assertTrue(table.is_active(0))
        self.assertFalse(table.is_active(1))
        self.assertFalse(table.is_active(2))
        self.assertFalse(table.is_active(3))
        self.assertFalse(table.is_active(4))
        self.assertFalse(table.is_active(5))
        self.assertTrue(table.is_occupied(0))
        self.assertTrue(table.is_occupied(1))
        self.assertTrue(table.is_occupied(2))
        self.assertFalse(table.is_occupied(3))
        self.assertFalse(table.is_occupied(4))
        self.assertFalse(table.is_occupied(5))
        table.stop()
        thread.join()

    def test_fold(self) -> None:

        def callback(table: Table, operation: Operation | None) -> None:
            if table.state is not None and table.state.can_fold():
                turn_index = table.turn_index

                assert turn_index is not None

                seat_index = table.get_seat_index(turn_index)
                player_name = table.player_names[seat_index]

                assert player_name is not None

                table.fold(player_name)

            button_indices.add(table.button_index)

            for i in table.seat_indices:
                starting_stacks[i].add(table.starting_stacks[i])

        table = self.create_table_a(callback)
        button_indices = set[int | None]()
        starting_stacks = [set[int | None]() for _ in table.seat_indices]
        thread = Thread(target=table.run)

        thread.start()
        table.connect('1', 1, 200)
        table.connect('2', 2, 80)
        table.connect('5', 5, 100)
        sleep(self.EPOCH_TIMEOUT)
        self.assertEqual(button_indices, {None, 1, 2, 5})
        self.assertEqual(
            starting_stacks,
            [
                {None},
                {None, 200, 201},
                {None, 79, 80},
                {None},
                {None},
                {None, 100, 101},
            ],
        )
        table.buy_in_rebuy_top_off_or_rat_hole('1', -1)
        table.buy_in_rebuy_top_off_or_rat_hole('2', 200)
        table.buy_in_rebuy_top_off_or_rat_hole('5', self.BUY_IN_RANGE.stop)
        sleep(self.EPOCH_TIMEOUT)
        self.assertEqual(button_indices, {None, 1, 2, 5})
        self.assertTrue(
            starting_stacks[2] == {None, 79, 80, 200, 201}
            or starting_stacks[2] == {None, 79, 80, 199, 200}
        )
        self.assertEqual(
            starting_stacks,
            [
                {None},
                {None, 200, 201},
                starting_stacks[2],
                {None},
                {None},
                {None, 100, 101},
            ],
        )
        table.stop()
        thread.join()

    def test_check_or_call(self) -> None:

        def callback(table: Table, operation: Operation | None) -> None:
            if table.state is not None:
                turn_index = table.turn_index

                if turn_index is not None:
                    seat_index = table.get_seat_index(turn_index)
                    player_name = table.player_names[seat_index]

                    assert player_name is not None

                    if table.state.can_post_bring_in():
                        table.post_bring_in(player_name)
                    elif table.state.can_check_or_call():
                        table.check_or_call(player_name)
                    elif table.state.can_show_or_muck_hole_cards():
                        table.show_or_muck_hole_cards(player_name)

        table = self.create_table_b(callback)
        thread = Thread(target=table.run)

        thread.start()
        table.connect('0', 0, 200)
        table.connect('3', 3, 200)
        table.connect('4', 4, 200)
        sleep(self.EPOCH_TIMEOUT)
        table.stop()
        thread.join()

    def test_all_in(self) -> None:

        def callback(table: Table, operation: Operation | None) -> None:
            if table.state is not None:
                turn_index = table.turn_index

                if turn_index is not None:
                    seat_index = table.get_seat_index(turn_index)
                    player_name = table.player_names[seat_index]

                    assert player_name is not None

                    if table.state.can_stand_pat_or_discard():
                        table.stand_pat_or_discard(player_name)
                    elif table.state.can_complete_bet_or_raise_to():
                        table.complete_bet_or_raise_to(
                            player_name,
                            (
                                table
                                .state
                                .max_completion_betting_or_raising_to_amount
                            ),
                        )
                    elif table.state.can_check_or_call():
                        table.check_or_call(player_name)

            for i in table.seat_indices:
                if (
                    table.is_occupied(i)
                    and (
                        table.buy_in_rebuy_top_off_or_rat_holing_amounts[i]
                        is None
                    )
                ):
                    player_name = table.player_names[i]

                    assert player_name is not None

                    table.buy_in_rebuy_top_off_or_rat_hole(player_name, 200)

        table = self.create_table_c(callback)
        thread = Thread(target=table.run)

        thread.start()
        table.connect('0', 0, 200)
        table.connect('1', 1, 200)
        table.connect('2', 2, 200)
        sleep(self.EPOCH_TIMEOUT)
        table.stop()
        thread.join()


if __name__ == '__main__':
    main()
