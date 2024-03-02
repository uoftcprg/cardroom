from threading import Thread

from django.apps import AppConfig


class CardroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cardroom'
    thread = None

    def ready(self) -> None:
        from cardroom.gamemaster import mainloop

        __import__('cardroom.signals')

        self.thread = Thread(target=mainloop, daemon=True)

        self.thread.start()
