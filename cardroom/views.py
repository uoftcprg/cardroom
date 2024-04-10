from typing import Any

from django.http import JsonResponse
from django.views.generic import DetailView
from rest_framework.viewsets import ModelViewSet

from cardroom.models import CashGame, HandHistory, Poker
from cardroom.serializers import (
    CashGameSerializer,
    HandHistorySerializer,
    PokerSerializer,
)
from cardroom.utilities import get_style, serialize


class CashGameViewSet(ModelViewSet):  # type: ignore[type-arg]
    queryset = CashGame.objects.all()
    serializer_class = CashGameSerializer


class HandHistoryViewSet(ModelViewSet):  # type: ignore[type-arg]
    queryset = HandHistory.objects.all()
    serializer_class = HandHistorySerializer


class PokerViewSet(ModelViewSet):  # type: ignore[type-arg]
    queryset = Poker.objects.all()
    serializer_class = PokerSerializer


class CashGameFeltView(DetailView):  # type: ignore[type-arg]
    model = CashGame
    template_name = 'cardroom/cashgame_felt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['style'] = serialize(get_style())
        frames = self.object.get_frames()
        context['frame'] = serialize(frames.get(self.request.user, frames['']))

        return context


class HandHistoryFeltView(DetailView):  # type: ignore[type-arg]
    model = HandHistory
    template_name = 'cardroom/handhistory_felt.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['style'] = serialize(get_style())
        context['frames'] = serialize(self.object.frames)

        return context


class CashGameFrameView(DetailView):  # type: ignore[type-arg]
    model = CashGame

    def render_to_response(
            self,
            context: dict[str, Any],
            **response_kwargs: Any,
    ) -> JsonResponse:
        frames = self.object.get_frames()

        return JsonResponse(
            serialize(frames.get(self.request.user, frames[''])),
            safe=False,
        )


class HandHistoryFramesView(DetailView):  # type: ignore[type-arg]
    model = HandHistory

    def render_to_response(
            self,
            context: dict[str, Any],
            **response_kwargs: Any,
    ) -> JsonResponse:
        return JsonResponse(serialize(self.object.frames), safe=False)
