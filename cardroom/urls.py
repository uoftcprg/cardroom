from django.contrib import admin
from django.urls import include, path, URLPattern, URLResolver
from rest_framework.routers import DefaultRouter

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_admin, get_auth, get_felt
from cardroom.views import (
    CashGameDetailView,
    CashGameViewSet,
    HandHistoryDetailView,
    HandHistoryViewSet,
    PokerViewSet,
    TableViewSet,
)

app_name: str = CardroomConfig.name
router = DefaultRouter()
urlpatterns: list[URLPattern | URLResolver] = []

router.register('poker', PokerViewSet)
router.register('table', TableViewSet)
router.register('cash-game', CashGameViewSet)
router.register('hand-history', HandHistoryViewSet)

if get_admin():
    urlpatterns.append(path('admin/', admin.site.urls))

if get_auth():
    urlpatterns.append(path('api-auth/', include('rest_framework.urls')))

if get_felt():
    urlpatterns.append(
        path(
            'felt/cash-game/<int:pk>/',
            CashGameDetailView.as_view(),
            name='felt_cash_game_detail',
        ),
    )
    urlpatterns.append(
        path(
            'felt/hand-history/<int:pk>/',
            HandHistoryDetailView.as_view(),
            name='felt_hand_history_detail',
        ),
    )

urlpatterns.append(path('', include(router.urls)))
