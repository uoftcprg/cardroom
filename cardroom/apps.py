from django.apps import AppConfig
from django.db import OperationalError


class CardroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cardroom'

    def ready(self) -> None:
        from cardroom.models import CashGame
        from cardroom.gamemaster import set_controller

        __import__('cardroom.signals')

        try:
            cash_games = list(CashGame.objects.all())
        except OperationalError:
            cash_games = []

        for cash_game in cash_games:
            set_controller(cash_game)
