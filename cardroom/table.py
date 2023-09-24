From collections.abc import Callable
from dataclasses import dataclass
from threading import Timer, Thread
from typing import Any


@dataclass
class Table:
    seat_count: int
    timebank: float
    idle_timeout: float
    ante_posting_timeout: float
    bet_collection_timeout: float
    blind_or_straddle_posting_timeout: float
    card_burning_timeout: float
    hole_dealing_timeout: float
    board_dealing_timeout: float
    standing_pat_timeout: float
    folding_timeout: float
    checking_timeout: float
    bring_in_posting_timeout: float
    hole_cards_showing_or_mucking_timeout: float
    hand_killing_timeout: float
    chips_pushing_timeout: float
    chips_pulling_timeout: float
    callback: Callable
    seat_indices: list[int] = field(init=False, default_factory=list)
    player_names: list[str] = field(init=False, default_factory=list)
    player_indices: list[int] = field(init=False, default_factory=list)
    time_banks: list[float | None] = field(init=False, default_factory=list)
    idle_statuses: list[bool] = field(init=False, default_factory=list)
    state: State | None = field(init=False, default=None)
    timers: list[Timer] = field(init=False, default_factory=list)

    def mainloop(self) -> None:
        pass

    def take_seat(
            self,
            player_name: str,
            seat_index: int,
    ):
        pass

    def leave_seat(
            self,
            player_name: str,
            seat_index: int,
    ):
        pass

    def idle(

    def stand_pat_or_discard(
            self,
            player_name: str,
            cards: CardsLike = None,
    ) -> None:
        pass

    def fold(self, player_name: str) -> None:
        pass

    def check_or_call(self, player_name: str) -> None:
        pass

    def post_bring_in(self, player_index: str) -> None:
        pass

    def complete_bet_or_raise_to(
            self,
            player_name: str,
            amount: int | None = None,
    ) -> None:
        pass

    def show_or_muck_hole_cards(
            self,
            player_name: str,
            status: bool | None = None,
    ) -> None:
        pass

    def _schedule(
            self,
            timeout: float,
            method: Callable[..., Any],
            *args: Any,
            **kwargs: Any,
    ):
        pass

    def _take_seat(
            self,
            player_name: str,
            seat_index: int,
    ):
        pass

    def _leave_seat(
            self,
            player_name: str,
            seat_index: int,
    ):
        pass

    def _idle(
            self,
            player_name: str,
    ):
        pass

    def _resume(
            self,
            player_name: str,
    ):
        pass

    def _stand_pat_or_discard(
            self,
            player_name: str,
            cards: CardsLike = None,
    ) -> None:
        pass

    def _fold(self, player_name: str) -> None:
        pass

    def _check_or_call(self, player_name: str) -> None:
        pass

    def _post_bring_in(self, player_index: str) -> None:
        pass

    def _complete_bet_or_raise_to(
            self,
            player_name: str,
            amount: int | None = None,
    ) -> None:
        pass

    def _show_or_muck_hole_cards(
            self,
            player_name: str,
            status: bool | None = None,
    ) -> None:
        pass
