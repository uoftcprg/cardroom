from warnings import resetwarnings, simplefilter

from django.test import SimpleTestCase
from pokerkit import FixedLimitRazz, NoLimitTexasHoldem, State

from cardroom.table import Table


class TableTestCase(SimpleTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        simplefilter('ignore')

    @classmethod
    def tearDownClass(cls) -> None:
        resetwarnings()

    def create_nt_table(self) -> Table:
        return Table(
            NoLimitTexasHoldem((), False, {1: 3}, [1, 2], 2),
            6,
            80,
            200,
        )

    def create_fr_table(self) -> Table:
        return Table(
            FixedLimitRazz((), True, 1, 1, 4, 8),
            6,
            80,
            200,
        )

    def terminate(self, state: State) -> None:
        while state.status:
            if state.can_post_ante():
                state.post_ante()
            elif state.can_post_blind_or_straddle():
                state.post_blind_or_straddle()
            elif state.can_collect_bets():
                state.collect_bets()
            elif state.can_burn_card():
                state.burn_card()  # pragma: no cover
            elif state.can_deal_board():
                state.deal_board()  # pragma: no cover
            elif state.can_deal_hole():
                state.deal_hole()
            elif state.can_stand_pat_or_discard():
                state.stand_pat_or_discard()  # pragma: no cover
            elif state.can_fold():
                state.fold()
            elif state.can_check_or_call():
                state.check_or_call()  # pragma: no cover
            elif state.can_post_bring_in():
                state.post_bring_in()
            elif state.can_complete_bet_or_raise_to():
                state.complete_bet_or_raise_to()  # pragma: no cover
            elif state.can_show_or_muck_hole_cards():
                state.show_or_muck_hole_cards()  # pragma: no cover
            elif state.can_kill_hand():
                state.kill_hand()  # pragma: no cover
            elif state.can_push_chips():
                state.push_chips()
            elif state.can_pull_chips():
                state.pull_chips()

    def test_game_changing(self) -> None:
        table = self.create_nt_table()
        game0 = table.game
        game1 = NoLimitTexasHoldem((), True, 0, [1, 2], 2)

        self.assertTrue(table.can_change_game(game0))
        self.assertTrue(table.can_change_game(game1))
        table.change_game(game1)
        self.assertTrue(table.can_change_game(game0))
        self.assertTrue(table.can_change_game(game1))
        self.assertIsNot(table.game, game0)
        self.assertIs(table.game, game1)

    def test_state_construction_and_state_deconstruction(self) -> None:
        table = self.create_nt_table()

        self.assertFalse(table.can_construct_state())
        table.join('u0', 4)
        self.assertFalse(table.can_construct_state())
        table.join('u1', 5)
        self.assertFalse(table.can_construct_state())
        table.buy_rebuy_top_off_or_rat_hole('u0', 200)
        self.assertFalse(table.can_construct_state())
        table.buy_rebuy_top_off_or_rat_hole('u1', 200)
        self.assertTrue(table.can_construct_state())
        table.sit_out('u0')
        self.assertFalse(table.can_construct_state())
        table.be_back('u0')
        self.assertTrue(table.can_construct_state())
        table.join('u2', 3)
        self.assertTrue(table.can_construct_state())
        table.join('u3', 0)
        self.assertTrue(table.can_construct_state())
        self.assertFalse(table.can_destroy_state())

        u0_indices = set()
        u2_indices = set()

        table.construct_state()

        assert table.state is not None

        u0_indices.add(table.get_seat('u0').player_index)
        u2_indices.add(table.get_seat('u2').player_index)
        self.assertEqual(table.state.starting_stacks, (200,) * 2)
        self.assertEqual(table.state.player_count, 2)
        self.assertFalse(table.can_destroy_state())
        self.terminate(table.state)
        self.assertTrue(table.can_destroy_state())
        table.destroy_state()

        table.construct_state()

        assert table.state is not None

        u0_indices.add(table.get_seat('u0').player_index)
        u2_indices.add(table.get_seat('u2').player_index)
        self.assertNotEqual(table.state.starting_stacks, (200,) * 2)
        self.assertEqual(table.state.player_count, 2)
        table.buy_rebuy_top_off_or_rat_hole('u2', 200)
        self.terminate(table.state)
        table.buy_rebuy_top_off_or_rat_hole('u3', 200)
        table.destroy_state()

        table.construct_state()

        assert table.state is not None

        u0_indices.add(table.get_seat('u0').player_index)
        u2_indices.add(table.get_seat('u2').player_index)
        self.terminate(table.state)
        table.destroy_state()

        table.construct_state()

        assert table.state is not None

        u0_indices.add(table.get_seat('u0').player_index)
        u2_indices.add(table.get_seat('u2').player_index)
        self.assertEqual(table.state.player_count, 4)
        self.terminate(table.state)
        table.buy_rebuy_top_off_or_rat_hole('u0', 200)
        table.buy_rebuy_top_off_or_rat_hole('u3', 200)
        table.destroy_state()

        table.buy_rebuy_top_off_or_rat_hole('u1', 200)
        table.buy_rebuy_top_off_or_rat_hole('u2', 100)
        table.buy_rebuy_top_off_or_rat_hole('u2', 200)

        table.construct_state()

        assert table.state is not None

        table.buy_rebuy_top_off_or_rat_hole('u0', 100)
        u0_indices.add(table.get_seat('u0').player_index)
        u2_indices.add(table.get_seat('u2').player_index)
        self.assertEqual(table.state.starting_stacks, (200,) * 4)
        self.terminate(table.state)
        table.destroy_state()

        self.assertNotIn(None, u0_indices)
        self.assertIn(None, u2_indices)
        self.assertGreaterEqual(len(u0_indices), 2)
        self.assertGreaterEqual(len(u0_indices), 3)

        table = self.create_fr_table()

        table.join('u0', 0)
        table.join('u1', 1)
        table.join('u2', 2)
        table.join('u3', 3)
        table.buy_rebuy_top_off_or_rat_hole('u0', 200)
        table.buy_rebuy_top_off_or_rat_hole('u1', 200)

        table.construct_state()

        assert table.state is not None

        self.assertEqual(table.get_seat('u0').player_index, 0)
        self.assertEqual(table.get_seat('u1').player_index, 1)
        self.assertEqual(table.get_seat('u2').player_index, None)
        self.assertEqual(table.get_seat('u3').player_index, None)
        self.terminate(table.state)
        table.destroy_state()

        table.construct_state()

        assert table.state is not None

        self.assertEqual(table.get_seat('u0').player_index, 0)
        self.assertEqual(table.get_seat('u1').player_index, 1)
        self.assertEqual(table.get_seat('u2').player_index, None)
        self.assertEqual(table.get_seat('u3').player_index, None)
        table.buy_rebuy_top_off_or_rat_hole('u2', 200)
        self.terminate(table.state)
        table.buy_rebuy_top_off_or_rat_hole('u3', 200)
        table.destroy_state()

        table.construct_state()

        assert table.state is not None

        self.assertEqual(table.get_seat('u0').player_index, 0)
        self.assertEqual(table.get_seat('u1').player_index, 1)
        self.assertEqual(table.get_seat('u2').player_index, 2)
        self.assertEqual(table.get_seat('u3').player_index, 3)
        self.terminate(table.state)
        table.destroy_state()

    def test_sitting_and_leaving(self) -> None:
        table = self.create_nt_table()

        self.assertTrue(table.can_join('u0', 4))
        table.join('u0', 4)
        self.assertFalse(table.can_join('u0', 4))
        self.assertFalse(table.can_join('u0', 5))
        self.assertFalse(table.can_join('u1', 4))
        self.assertTrue(table.can_join('u1', 5))
        table.join('u1', 5)
        self.assertFalse(table.can_join('u2', 4))
        self.assertTrue(table.can_leave('u0'))
        table.leave('u0')
        self.assertTrue(table.can_join('u2', 4))
        table.join('u2', 4)
        self.assertFalse(table.can_leave('u0'))
        table.join('u0', 2)
        self.assertTrue(table.can_leave('u0'))
        table.leave('u0')

    def test_sitting_out_and_being_back(self) -> None:
        table = self.create_nt_table()

        self.assertFalse(table.can_sit_out('u0'))
        self.assertFalse(table.can_be_back('u0'))
        table.join('u0', 4)
        self.assertTrue(table.can_sit_out('u0'))
        self.assertFalse(table.can_be_back('u0'))
        table.sit_out('u0')
        self.assertFalse(table.can_sit_out('u0'))
        self.assertTrue(table.can_be_back('u0'))
        table.be_back('u0')
        self.assertTrue(table.can_sit_out('u0'))
        self.assertFalse(table.can_be_back('u0'))
        table.leave('u0')
        self.assertFalse(table.can_sit_out('u0'))
        self.assertFalse(table.can_be_back('u0'))

    def test_rebuying_or_topping_off(self) -> None:
        table = self.create_nt_table()

        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 200))
        table.join('u0', 5)
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 40))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 100))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 150))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 200))
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 400))
        table.buy_rebuy_top_off_or_rat_hole('u0', 150)
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 40))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 100))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 150))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 200))
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 400))
        table.buy_rebuy_top_off_or_rat_hole('u0', 200)
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 40))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 100))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 150))
        self.assertTrue(table.can_buy_rebuy_top_off_or_rat_hole('u0', 200))
        self.assertFalse(table.can_buy_rebuy_top_off_or_rat_hole('u0', 400))
