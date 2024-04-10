from django.contrib import admin
from django.urls import include, path, URLPattern, URLResolver
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_admin, get_auth, get_felt
from cardroom.views import (
    CashGameFeltView,
    CashGameFrameView,
    CashGameViewSet,
    HandHistoryFeltView,
    HandHistoryFramesView,
    HandHistoryViewSet,
    PokerViewSet,
)

app_name: str = CardroomConfig.name
router: DefaultRouter = DefaultRouter()

router.register('cash-games', CashGameViewSet)
router.register('hand-histories', HandHistoryViewSet)
router.register('games', PokerViewSet)

urlpatterns: list[URLPattern | URLResolver] = [
    path('', include(router.urls)),
    path(
        'cash-games/<int:pk>/frame/',
        CashGameFrameView.as_view(),
        name='cashgame_frame',
    ),
    path(
        'hand-histories/<int:pk>/frames/',
        HandHistoryFramesView.as_view(),
        name='handhistory_frames',
    ),
]

if get_auth():
    urlpatterns.append(path('auth/', include('rest_framework.urls')))
    urlpatterns.append(path('auth/token/', obtain_auth_token))

if get_admin():
    urlpatterns.append(path('admin/', admin.site.urls))

if get_felt():
    urlpatterns.append(
        path(
            'cash-games/<int:pk>/felt/',
            CashGameFeltView.as_view(),
            name='cashgame_felt',
        ),
    )
    urlpatterns.append(
        path(
            'hand-histories/<int:pk>/felt/',
            HandHistoryFeltView.as_view(),
            name='handhistory_felt',
        ),
    )
