from dataclasses import asdict
from typing import Any

from django.http import JsonResponse
from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from cardroom.felt import Settings, Data
from cardroom.gamemaster import get_data
from cardroom.models import CashGame, HandHistory, Poker, Table
from cardroom.serializers import (
    CashGameSerializer,
    HandHistorySerializer,
    PokerSerializer,
    TableSerializer,
)


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
    template_name = 'cardroom/cash-game.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        data = get_data(self.object)
        data = asdict(data.get(self.request.user.username, data[None]))
        context['data'] = data

        return context


class HandHistoryFeltView(DetailView):
    model = HandHistory
    template_name = 'cardroom/hand-history.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        data = tuple(map(asdict, Data.from_hand_history(self.object.load())))
        context['data'] = data

        return context


class CashGameFeltDataView(DetailView):
    model = CashGame

    def render_to_response(self, context, **response_kwargs):
        data = get_data(self.object)
        data = asdict(data.get(self.request.user.username, data[None]))

        return JsonResponse(data)


class HandHistoryFeltDataView(DetailView):
    model = HandHistory

    def render_to_response(self, context, **response_kwargs):
        data = tuple(map(asdict, Data.from_hand_history(self.object.load())))

        return JsonResponse(data, safe=False)
