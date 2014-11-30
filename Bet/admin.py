from django.contrib import admin
from django.contrib.admin.helpers import ActionForm
from django import forms
from django.contrib import messages
from django.shortcuts import get_object_or_404
from Bet.models import *


class GameBetAdmin(admin.ModelAdmin):

    def update_winner(modeladmin, request, queryset):
        bets = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)

        for bet_id in bets:
            bet = get_object_or_404(GameBet, id=bet_id)
            if bet.winner is None:
                messages.error(request, "[" + bet.game.name + "] " + bet.team1.name + " vs " + bet.team2.name + ": Does not have a winner, please edit the bet and select one")
            elif bet.payed:
                messages.warning(request, "[" + bet.game.name + "] " + bet.team1.name + " vs " + bet.team2.name + ": Have already been payed out.")
            else:
                bet.pay_out()
                messages.success(request, "[" + bet.game.name + "] " + bet.team1.name + " vs " + bet.team2.name + ": Have been payed to the clients.")

    update_winner.short_description = 'Payout bet (must have a winner)'
    actions = [update_winner]


admin.site.register(GameBetEntry)
admin.site.register(GameBet, GameBetAdmin)
