from threading import Thread

from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError
from django.conf import settings


class CardroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cardroom'
    thread = None

    def ready(self) -> None:
        # Check if CARDROOM_MAINLOOP is set and True
        if getattr(settings, 'CARDROOM_MAINLOOP', False):
            from cardroom.gamemaster import mainloop
            from cardroom.models import CashGame

            __import__('cardroom.signals')

            self.thread = Thread(target=mainloop, daemon=True)

            self.thread.start()
