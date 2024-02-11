from dataclasses import asdict
from typing import Any

from django.http import JsonResponse
from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from cardroom.models import CashGame, HandHistory, Poker, Table
from cardroom.serializers import (
    CashGameSerializer,
    HandHistorySerializer,
    PokerSerializer,
    TableSerializer,
)
from cardroom.utilities import get_configuration, serialize


class PokerViewSet(ModelViewSet):
    queryset = Poker.objects.all()
    serializer_class = PokerSerializer


class TableViewSet(ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer


class CashGameViewSet(ModelViewSet):
    queryset = CashGame.objects.all()
    serializer_class = CashGameSerializer


class HandHistoryViewSet(ModelViewSet):
    queryset = HandHistory.objects.all()
    serializer_class = HandHistorySerializer


class CashGameFeltView(DetailView):
    model = CashGame
    template_name = 'cardroom/cashgame_felt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['configuration'] = asdict(get_configuration())
        context['frame'] = asdict(self.object.get_frame(self.request.user))

        return context


class HandHistoryFeltView(DetailView):
    model = HandHistory
    template_name = 'cardroom/handhistory_felt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['configuration'] = asdict(get_configuration())
        context['frames'] = serialize(self.object.frames)

        return context


class CashGameFrameView(DetailView):
    model = CashGame

    def render_to_response(
            self,
            context: dict[str, Any],
            **response_kwargs: Any,
    ) -> JsonResponse:
        return JsonResponse(asdict(self.object.get_frame(self.request.user)))


class HandHistoryFramesView(DetailView):
    model = HandHistory

    def render_to_response(
            self,
            context: dict[str, Any],
            **response_kwargs: Any,
    ) -> JsonResponse:
        return JsonResponse(serialize(self.object.frames), safe=False)
