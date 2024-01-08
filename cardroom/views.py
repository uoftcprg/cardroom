from dataclasses import asdict
from typing import Any

from django.views.generic import DetailView

from cardroom.models import CashGame, HandHistory
from cardroom.felt import Settings, Data


class CashGameDetailView(DetailView):  # type: ignore[type-arg]
    model = CashGame


class HandHistoryDetailView(DetailView):  # type: ignore[type-arg]
    model = HandHistory

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['raw_settings'] = asdict(Settings())
        context['raw_data'] = tuple(
            map(asdict, Data.from_hand_history(self.object.load())),
        )

        return context
