from dataclasses import asdict
from typing import Any

from django.views.generic import DetailView

from cardroom.models import CashGame, HandHistory
from cardroom.felt import Settings, Data
from cardroom.gamemaster import get_data


class CashGameDetailView(DetailView):  # type: ignore[type-arg]
    model = CashGame

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        data = get_data(self.object)  # type: ignore[no-untyped-call]
        context['data'] = (asdict(data),)

        return context


class HandHistoryDetailView(DetailView):  # type: ignore[type-arg]
    model = HandHistory

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['settings'] = asdict(Settings())
        context['data'] = tuple(
            map(asdict, Data.from_hand_history(self.object.load())),
        )

        return context
