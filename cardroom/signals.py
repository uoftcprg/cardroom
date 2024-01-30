from django.db.models.signals import post_save
from django.dispatch import receiver

from cardroom.gamemaster import set_controller
from cardroom.models import CashGame


@receiver(post_save, sender=CashGame)
def set_cash_game_controller(
        sender,
        instance=None,
        created=False,
        **kwargs,
):
    set_controller(instance)
