from rest_framework.request import Request
from rest_framework.serializers import (
    HyperlinkedModelSerializer,
    SerializerMethodField,
)

from cardroom.models import CashGame, HandHistory, Poker, Table
from cardroom.utilities import get_felt


class CardroomHyperlinkedModelSerializer(HyperlinkedModelSerializer):
    @property
    def request(self) -> Request:
        return self.context['request']


class PokerSerializer(CardroomHyperlinkedModelSerializer):
    class Meta:
        model = Poker
        fields = '__all__'


class TableSerializer(CardroomHyperlinkedModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class CashGameSerializer(CardroomHyperlinkedModelSerializer):
    frame_url = SerializerMethodField()

    def get_frame_url(self, obj: CashGame) -> str:
        return self.request.build_absolute_uri(obj.get_frame_url())

    websocket_url = SerializerMethodField()

    def get_websocket_url(self, obj: CashGame) -> str:
        url = self.request.build_absolute_uri(obj.get_websocket_url())

        if url.startswith('https:'):
            url = f'wss:{url[6:]}'
        elif url.startswith('http:'):
            url = f'ws:{url[5:]}'
        else:
            raise AssertionError

        return url

    if get_felt():
        felt_url = SerializerMethodField()

        def get_felt_url(self, obj: CashGame) -> str:
            return self.request.build_absolute_uri(obj.get_felt_url())

    class Meta:
        model = CashGame
        fields = '__all__'


class HandHistorySerializer(CardroomHyperlinkedModelSerializer):
    url_field_name = 'url_'
    frames_url = SerializerMethodField()

    def get_frames_url(self, obj: HandHistory) -> str:
        return self.request.build_absolute_uri(obj.get_frames_url())

    if get_felt():
        felt_url = SerializerMethodField()

        def get_felt_url(self, obj: HandHistory) -> str:
            return self.request.build_absolute_uri(obj.get_felt_url())

    class Meta:
        model = HandHistory
        fields = '__all__'
