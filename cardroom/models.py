from __future__ import annotations

from collections.abc import Iterator
from dataclasses import fields

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import NoReverseMatch, reverse
from pokerkit import ValuesLike
import pokerkit

from cardroom.apps import CardroomConfig
from cardroom.utilities import get_divmod, get_parse_value, get_tzinfo
import cardroom.controller as controller
import cardroom.table as table


class Variant(models.TextChoices):
    FIXED_LIMIT_TEXAS_HOLDEM = 'FT', _('Fixed-limit Texas hold \'em')
    NO_LIMIT_TEXAS_HOLDEM = 'NT', _('No-limit Texas hold \'em')
    NO_LIMIT_SHORT_DECK_HOLDEM = 'NS', _('No-limit short-deck hold \'em')
    POT_LIMIT_OMAHA_HOLDEM = 'PO', _('Pot-limit Omaha hold \'em')
    FIXED_LIMIT_OMAHA_HOLDEM_HIGH_LOW_SPLIT_EIGHT_OR_BETTER = (
        'FO/8',
        _('Fixed-limit Omaha hold \'em high/low-split eight-or-better'),
    )
    FIXED_LIMIT_SEVEN_CARD_STUD = 'F7S', _('Fixed-limit seven card stud')
    FIXED_LIMIT_SEVEN_CARD_STUD_HIGH_LOW_SPLIT_EIGHT_OR_BETTER = (
        'F7S/8',
        _('Fixed-limit seven card stud high/low-split eight-or-better'),
    )
    FIXED_LIMIT_RAZZ = 'FR', _('Fixed-limit razz')
    NO_LIMIT_DEUCE_TO_SEVEN_LOWBALL_SINGLE_DRAW = (
        'N2L1D',
        _('No-limit deuce-to-seven lowball single draw'),
    )
    FIXED_LIMIT_DEUCE_TO_SEVEN_LOWBALL_TRIPLE_DRAW = (
        'F2L3D',
        _('Fixed-limit deuce-to-seven lowball triple draw'),
    )
    FIXED_LIMIT_BADUGI = 'FB', _('Fixed-limit badugi')


class Poker(models.Model):
    name = models.CharField(max_length=255, unique=True)
    variant = models.CharField(max_length=255, choices=Variant.choices)
    ante_trimming_status = models.BooleanField(default=False)
    raw_antes = models.JSONField()
    raw_blinds_or_straddles = models.JSONField(blank=True, null=True)
    bring_in = models.JSONField(blank=True, null=True)
    small_bet = models.JSONField(blank=True, null=True)
    big_bet = models.JSONField(blank=True, null=True)
    min_bet = models.JSONField(blank=True, null=True)

    def __str__(self) -> str:
        return self.name

    def load(self) -> pokerkit.Poker:

        def clean(raw_values: ValuesLike) -> ValuesLike:
            if isinstance(raw_values, dict):
                raw_values = dict(
                    zip(map(int, raw_values.keys()), raw_values.values()),
                )

            return raw_values

        kwargs = {
            'automations': (),
            'ante_trimming_status': self.ante_trimming_status,
            'raw_antes': clean(self.raw_antes),
            'raw_blinds_or_straddles': clean(self.raw_blinds_or_straddles),
            'bring_in': self.bring_in,
            'small_bet': self.small_bet,
            'big_bet': self.big_bet,
            'min_bet': self.min_bet,
            'divmod': get_divmod(),
        }

        for key, value in tuple(kwargs.items()):
            if value is None:
                kwargs.pop(key)

        return pokerkit.HandHistory.game_types[self.variant](**kwargs)

    class Meta:
        verbose_name_plural = 'poker'


class Table(models.Model):
    game = models.ForeignKey(Poker, models.PROTECT)
    seat_count = models.PositiveBigIntegerField()
    min_starting_stack = models.JSONField(blank=True, null=True)
    max_starting_stack = models.JSONField(blank=True, null=True)

    def load(self) -> table.Table:
        return table.Table(
            self.game.load(),
            self.seat_count,
            self.min_starting_stack,
            self.max_starting_stack,
        )


class Controller(models.Model):
    name = models.CharField(max_length=255, unique=True)
    time_bank = models.FloatField()
    time_bank_increment = models.FloatField()
    state_construction_timeout = models.FloatField()
    state_destruction_timeout = models.FloatField()
    idle_timeout = models.FloatField()
    standing_pat_timeout = models.FloatField()
    betting_timeout = models.FloatField()
    hole_cards_showing_or_mucking_timeout = models.FloatField()

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class CashGame(Controller):
    table = models.ForeignKey(Table, models.PROTECT)

    def get_absolute_url(self, namespace: str = CardroomConfig.name) -> str:
        try:
            url = reverse(
                f'{namespace}:cash_game_detail',
                kwargs={'pk': self.pk},
            )
        except NoReverseMatch:
            url = reverse('cash_game_detail', kwargs={'pk': self.pk})

        return url

    def load(self) -> controller.CashGame:
        return controller.CashGame(
            self.name,
            self.time_bank,
            self.time_bank_increment,
            self.state_construction_timeout,
            self.state_destruction_timeout,
            self.idle_timeout,
            self.standing_pat_timeout,
            self.betting_timeout,
            self.hole_cards_showing_or_mucking_timeout,
            lambda _: None,  # TODO
            get_parse_value(),
            get_tzinfo(),
            self.table.load(),
        )


class HandHistory(models.Model):
    variant = models.CharField(max_length=255, choices=Variant.choices)
    ante_trimming_status = models.BooleanField(default=False)
    antes = models.JSONField()
    blinds_or_straddles = models.JSONField(blank=True, null=True)
    bring_in = models.JSONField(blank=True, null=True)
    small_bet = models.JSONField(blank=True, null=True)
    big_bet = models.JSONField(blank=True, null=True)
    min_bet = models.JSONField(blank=True, null=True)
    starting_stacks = models.JSONField()
    actions = models.JSONField()
    author = models.CharField(max_length=255, blank=True, null=True)
    event = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    time_zone = models.CharField(max_length=255, blank=True, null=True)
    day = models.PositiveBigIntegerField(blank=True, null=True)
    month = models.PositiveBigIntegerField(blank=True, null=True)
    year = models.PositiveBigIntegerField(blank=True, null=True)
    hand = models.PositiveBigIntegerField(blank=True, null=True)
    level = models.PositiveBigIntegerField(blank=True, null=True)
    seats = models.JSONField(blank=True, null=True)
    seat_count = models.PositiveBigIntegerField(blank=True, null=True)
    table = models.PositiveBigIntegerField(blank=True, null=True)
    players = models.JSONField(blank=True, null=True)
    finishing_stacks = models.JSONField(blank=True, null=True)
    currency = models.CharField(max_length=255, blank=True, null=True)
    time_limit = models.JSONField(blank=True, null=True)
    time_banks = models.JSONField(blank=True, null=True)

    @classmethod
    def get_field_names(cls) -> Iterator[str]:
        for field in fields(pokerkit.HandHistory):
            try:
                cls._meta.get_field(field.name)
            except FieldDoesNotExist:
                pass
            else:
                yield field.name

    def get_absolute_url(self, namespace: str = CardroomConfig.name) -> str:
        try:
            url = reverse(
                f'{namespace}:hand_history_detail',
                kwargs={'pk': self.pk},
            )
        except NoReverseMatch:
            url = reverse('hand_history_detail', kwargs={'pk': self.pk})

        return url

    @classmethod
    def dump(cls, hh: pokerkit.HandHistory) -> HandHistory:
        kwargs = {}

        for name in cls.get_field_names():
            kwargs[name] = getattr(hh, name)

        return cls(**kwargs)

    def load(self) -> pokerkit.HandHistory:
        kwargs = {}

        for name in type(self).get_field_names():
            kwargs[name] = getattr(self, name)

        return pokerkit.HandHistory(**kwargs)

    class Meta:
        verbose_name_plural = 'hand histories'
