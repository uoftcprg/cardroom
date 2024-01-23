from rest_framework.serializers import HyperlinkedModelSerializer

from cardroom.models import CashGame, HandHistory, Poker, Table


class PokerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Poker
        fields = '__all__'


class TableSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class CashGameSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = CashGame
        fields = '__all__'


class HandHistorySerializer(HyperlinkedModelSerializer):
    class Meta:
        model = HandHistory
        fields = '__all__'
