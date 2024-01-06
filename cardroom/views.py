from django.views.generic import DetailView

from cardroom.models import CashGame, HandHistory


class CashGameDetailView(DetailView):  # type: ignore[type-arg]
    model = CashGame


class HandHistoryDetailView(DetailView):  # type: ignore[type-arg]
    model = HandHistory
