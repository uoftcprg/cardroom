from django.apps import AppConfig


class CardroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cardroom'

    def ready(self) -> None:
        from cardroom.models import CashGame
        from cardroom.gamemaster import set_controller

        __import__('cardroom.signals')

        for cash_game in CashGame.objects.all():
            set_controller(cash_game)
