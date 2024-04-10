from django.contrib import admin

from cardroom.models import CashGame, HandHistory, Poker

admin.site.register(CashGame)
admin.site.register(HandHistory)
admin.site.register(Poker)
