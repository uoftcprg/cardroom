from django.urls import path, URLResolver

from cardroom.apps import CardroomConfig
from cardroom.consumers import CashGameConsumer

app_name: str = CardroomConfig.name
urlpatterns: list[URLResolver] = [
    path(
        'cash-games/<int:pk>/',
        CashGameConsumer.as_asgi(),
        name='cashgame_websocket',
    ),
]
