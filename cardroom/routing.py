from django.urls import path, URLResolver

from cardroom.consumers import CashGameConsumer

websocket_urlpatterns: list[URLResolver] = [
    path('cash-game/<int:pk>/', CashGameConsumer.as_asgi()),
]
