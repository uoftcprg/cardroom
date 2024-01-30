from django.db.models.signals import post_save
from django.dispatch import receiver

from cardroom.gamemaster import set_controller
from cardroom.models import CashGame


@receiver(post_save, sender=CashGame)
def cash_game_post_save(
        sender,
        instance,
        created,
        raw,
        using,
        update_fields,
        **kwargs,
):
    set_controller(instance)
