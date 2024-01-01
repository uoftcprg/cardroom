from django.contrib import admin

from cardroom.models import HandHistory, Table, Poker

admin.site.register(HandHistory)
admin.site.register(Table)
admin.site.register(Poker)
