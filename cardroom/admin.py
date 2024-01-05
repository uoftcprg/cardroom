from django.contrib import admin

from cardroom.models import CashGame, HandHistory, Poker, Table

admin.site.register(CashGame)
admin.site.register(HandHistory)
admin.site.register(Poker)
admin.site.register(Table)
