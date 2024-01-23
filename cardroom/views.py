from dataclasses import asdict
from typing import Any

from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from cardroom.felt import Settings, Data
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


class CashGameDetailView(DetailView):
    model = CashGame

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        context['data'] = (asdict(Data()),)

        return context


class HandHistoryDetailView(DetailView):
    model = HandHistory

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        context['data'] = tuple(
            map(asdict, Data.from_hand_history(self.object.load())),
        )

        return context
