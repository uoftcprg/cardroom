from django.test import SimpleTestCase
from pokerkit import NoLimitTexasHoldem

from cardroom.table import Table


class TableTestCase(SimpleTestCase):
    def create_nt_table(self) -> Table:
        return Table(
            NoLimitTexasHoldem((), False, {1: 3}, [1, 2], 2),
            6,
            80,
            200,
        )

    def test_game_changing(self) -> None:
        table = self.create_nt_table()
        game0 = table.game
        game1 = NoLimitTexasHoldem((), True, 0, [1, 2], 2)

        self.assertTrue(table.can_change_game)
        table.change_game(game1)
        self.assertTrue(table.can_change_game)
        self.assertIsNot(table.game, game0)
        self.assertIs(table.game, game1)

    def test_state_construction_and_state_deconstruction(self) -> None:
        pass

    def test_sitting_and_leaving(self) -> None:
        table = self.create_nt_table()

        self.assertTrue(table.can_sit('u0', 4))
        table.sit('u0', 4)
        self.assertFalse(table.can_sit('u0', 4))
        self.assertFalse(table.can_sit('u0', 5))
        self.assertFalse(table.can_sit('u1', 4))
        self.assertTrue(table.can_sit('u1', 5))
        table.sit('u1', 5)
        self.assertFalse(table.can_sit('u2', 4))
        self.assertTrue(table.can_leave('u0'))
        table.leave('u0')
        self.assertTrue(table.can_sit('u2', 4))
        table.sit('u2', 4)
        self.assertFalse(table.can_leave('u0'))
        table.sit('u0', 2)
        self.assertTrue(table.can_leave('u0'))
        table.leave('u0')

    def test_sitting_out_and_being_back(self) -> None:
        table = self.create_nt_table()

        self.assertFalse(table.can_sit_out('u0'))
        self.assertFalse(table.can_be_back('u0'))
        table.sit('u0', 4)
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

        self.assertFalse(table.can_rebuy_or_top_off('u0', 200))
        table.sit('u0', 5)
        self.assertFalse(table.can_rebuy_or_top_off('u0', 40))
        self.assertTrue(table.can_rebuy_or_top_off('u0', 100))
        self.assertTrue(table.can_rebuy_or_top_off('u0', 150))
        self.assertTrue(table.can_rebuy_or_top_off('u0', 200))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 400))
        table.rebuy_or_top_off('u0', 150)
        self.assertFalse(table.can_rebuy_or_top_off('u0', 40))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 100))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 150))
        self.assertTrue(table.can_rebuy_or_top_off('u0', 200))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 400))
        table.rebuy_or_top_off('u0', 200)
        self.assertFalse(table.can_rebuy_or_top_off('u0', 40))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 100))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 150))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 200))
        self.assertFalse(table.can_rebuy_or_top_off('u0', 400))
