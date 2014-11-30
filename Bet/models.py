from datetime import datetime
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import register
from Logging.models import BetSettleLog


class GameBet(models.Model):
    team1 = models.ForeignKey('Accounting.Team', related_name='Team 1')
    team2 = models.ForeignKey('Accounting.Team', related_name='Team 2')
    game_start = models.DateTimeField()
    bet_end = models.DateTimeField()
    min_amount = models.FloatField()
    max_amount = models.FloatField()
    maxEnterTimes = models.IntegerField()
    winner = models.ForeignKey('Accounting.Team', default=None, null=True, blank=True)
    game = models.ForeignKey('Accounting.Game')
    desc = models.TextField(help_text="Please enter this in HTML")
    payed = models.BooleanField(default=False)
    image = models.FileField(help_text="Should be 800x300")

    def __str__(self):
        return "[" + self.game.name + "] " + self.team1.name + " vs " + self.team2.name

    def get_small_desc(self):
        return self.desc[:25] + "..."

    def has_ended(self):
        if self.bet_end <= timezone.now():
            return True
        if self.winner is not None:
            return True

        return False

    def pay_out(self):
        # https://docs.google.com/spreadsheets/d/1daNy_kdUVPlumpK9WOYcqp8z9nC3VZQDNnrQJRMMnYE/edit?usp=sharing
        if not self.payed and self.winner is not None:
            all = GameBetEntry.objects.filter(bet=self)
            winners = GameBetEntry.objects.filter(bet=self, team=self.winner)
            winners2 = GameBetEntry.objects.filter(bet=self, team=self.winner)

            # we get the total amount in the pool
            total = 0.00
            for a in all:
                total = total + a.amount

            # we now get the total in the winnings pool, to calculate the % a winner will get of the total pool
            winnersTotal = 0
            for w in winners2:
                winnersTotal = winnersTotal + w.amount

            total_payed = 0.00

            for winner in winners:
                # we get the % of the winnings, this will be the % that the user wins from the total pool
                cutOfWinnersTotal = (winner.amount / winnersTotal) * 100

                # we now get the amount from the total that the user will win, and removes 10% that is our fee.
                winnings = (((total / 100) * cutOfWinnersTotal) / 100) * 90

                #winnings cannot be below the amount played, if its below then we dont take our cut, and simply payout the amount the the user gambled for.
                if winnings < winner.amount:
                    # we create a transaction for the user
                    winner.user.create_transaction(winner.amount, "Winnings from Bet: <a href='/bet/" + str(self.id) + "/'>#" + str(self.id) + "</a> - " + self.winner.name)
                    total_payed += winner.amount
                else:
                    # we create a transaction for the user
                    winner.user.create_transaction(winnings, "Winnings from Bet: <a href='/bet/" + str(self.id) + "/'>#" + str(self.id) + "</a> - " + self.winner.name)
                    total_payed += winnings

            self.payed = True
            self.save()

            our_cut = self.get_pool() - total_payed

            # log
            l = BetSettleLog(
                bet=self,
                date=datetime.now(),
                ourCut=our_cut,
            )
            l.save()

    def set_winner(self, team):
        self.winner = team
        self.save()
        self.pay_out()

    def get_pool(self):
        all = GameBetEntry.objects.filter(bet=self)

        total = 0
        for a in all:
            total = total + a.amount

        return total

    @register.filter
    def get_user_entries_bet(self, user):
        return len(GameBetEntry.objects.filter(bet=self,user=user))

    @register.filter
    def get_potential_1(self, team):
        all = GameBetEntry.objects.filter(bet=self)

        total = 0
        for a in all:
            total = total + a.amount

        played_on_team = GameBetEntry.objects.filter(bet=self, team=team)

        amount_on_team = 0
        for p in played_on_team:
            amount_on_team = amount_on_team + p.amount

        if amount_on_team > 0:
            cut_perc = (1 / amount_on_team) * 100

            return "{0:.2f}".format((total / 100) * cut_perc)
        else:
            return "{0:.2f}".format(1.00)

    @register.filter
    def get_potential_winnings(self, amount, team):
        all = GameBetEntry.objects.filter(bet=self)

        total = 0
        for a in all:
            total = total + a.amount

        played_on_team = GameBetEntry.objects.filter(bet=self, team=team)

        amount_on_team = 0
        for p in played_on_team:
            amount_on_team = amount_on_team + p.amount

        cut_perc = (amount / amount_on_team) * 100

        return (total / 100) * cut_perc

    def enter_bet(self, team, amount, user):
        if self.winner is not None:
            return False
        if self.bet_end <= timezone.now():
            return False
        if amount <= self.min_amount:
            return False
        if amount >= self.max_amount:
            return False
        user_enter_times = len(GameBetEntry.objects.filter(user=user, bet=self))
        if user_enter_times >= self.maxEnterTimes:
            return False
        if user.get_balance() < amount:
            return False

        transaction = user.create_transaction(-amount, "Payment for Bet: <a href='/bet/" + str(self.id) + "/'>#" + str(self.id) + "</a> - " + team.name)

        gameBet = GameBetEntry(
            bet=self,
            user=user,
            date=datetime.now(),
            amount=amount,
            team=team,
            transaction=transaction
        )
        gameBet.save()
        return True


class GameBetEntry(models.Model):
    bet = models.ForeignKey(GameBet)
    user = models.ForeignKey('Accounting.User')
    date = models.DateTimeField()
    amount = models.FloatField()
    team = models.ForeignKey('Accounting.Team')
    transaction = models.ForeignKey('Accounting.Transaction')

    def __str__(self):
        return self.user.email + ": $" + str(self.amount) + " on: " + self.bet.__str__()