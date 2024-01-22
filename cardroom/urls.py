from django.contrib import admin
from django.urls import path, URLPattern, URLResolver

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_admin_urls, get_views
from cardroom.views import CashGameDetailView, HandHistoryDetailView

app_name: str = CardroomConfig.name
urlpatterns: list[URLPattern | URLResolver] = []

if get_views():
    urlpatterns.append(
        path(
            'cash-game/<int:pk>/',
            CashGameDetailView.as_view(),
            name='cash_game_detail',
        ),
    )
    urlpatterns.append(
        path(
            'hand-history/<int:pk>/',
            HandHistoryDetailView.as_view(),
            name='hand_history_detail',
        ),
    )

if get_admin_urls():
    urlpatterns.append(path('', admin.site.urls))
