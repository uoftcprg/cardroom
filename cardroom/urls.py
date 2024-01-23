from django.contrib import admin
from django.urls import include, path, URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_admin, get_auth, get_felt
from cardroom.views import (
    CashGameFeltDataView,
    CashGameFeltView,
    CashGameViewSet,
    HandHistoryFeltDataView,
    HandHistoryFeltView,
    HandHistoryViewSet,
    PokerViewSet,
    TableViewSet,
)

app_name: str = CardroomConfig.name
router = DefaultRouter()
urlpatterns: list[URLPattern | URLResolver] = [
    path('cash-games/<int:pk>/felt/data/', CashGameFeltDataView.as_view()),
    path(
        'hand-histories/<int:pk>/felt/data/',
        HandHistoryFeltDataView.as_view(),
    ),
]

router.register('poker', PokerViewSet)
router.register('tables', TableViewSet)
router.register('cash-games', CashGameViewSet)
router.register('hand-histories', HandHistoryViewSet)

if get_admin():
    urlpatterns.append(path('admin/', admin.site.urls))

if get_auth():
    urlpatterns.append(path('api-auth/', include('rest_framework.urls')))

if get_felt():
    urlpatterns.append(
        path(
            'cash-games/<int:pk>/felt/',
            CashGameFeltView.as_view(),
            name='cash_game_felt',
        ),
    )
    urlpatterns.append(
        path(
            'hand-histories/<int:pk>/felt/',
            HandHistoryFeltView.as_view(),
            name='hand_history_felt',
        ),
    )

urlpatterns.append(path('', include(router.urls)))
