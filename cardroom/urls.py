from django.contrib import admin
from django.urls import path, URLPattern, URLResolver

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_admin_urls
from cardroom.views import CashGameDetailView, HandHistoryDetailView

app_name = CardroomConfig.name
urlpatterns: list[URLPattern | URLResolver] = [
    path(
        'cash-game/<int:pk>/',
        CashGameDetailView.as_view(),
        name='cash_game_detail',
    ),
    path(
        'hand-history/<int:pk>/',
        HandHistoryDetailView.as_view(),
        name='hand_history_detail',
    ),
]

if get_admin_urls():
    urlpatterns.append(path('', admin.site.urls))
