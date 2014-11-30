from datetime import datetime
from django.db import models
from django import forms
from Bet.models import *
from Raffle.models import *


class Game(models.Model):
    name = models.CharField(max_length=255, unique=True)
    icon = models.FileField()

    def __str__(self):
        return self.name

    def get_bets_amount(self):
        return len(GameBet.objects.filter(winner=None, game=self))

    def get_raffles_amount(self):
        return len(Raffle.objects.filter(endDate=None, game=self))


class Team(models.Model):
    name = models.CharField(max_length=255)
    logo = models.FileField()
    web = models.URLField()
    game = models.ForeignKey(Game)

    def __str__(self):
        return "[" + self.game.name + "] " + self.name


class User(models.Model):
    email = models.EmailField(max_length=255, unique=True)
    pwd = models.CharField(max_length=255)
    banned = models.BooleanField(default=False)

    def get_email_ob(self):
        return self.email.split('@')[0] + "@************.com"

    def get_balance(self):
        balance = 0
        for transaction in Transaction.objects.filter(user=self):
            balance = balance + transaction.amount
        return balance

    def create_transaction(self, amount, data):
        transaction = Transaction(
            user=self,
            amount=amount,
            time=datetime.now(),
            data=data
        )
        transaction.save()

        return transaction

    def get_raffels(self):
        return RaffleEntry.objects.filter(user=self).order_by('-date')

    def total_used_on_raffles(self):
        total = 0
        for userRaffle in RaffleEntry.objects.filter(user=self):
            total = total + userRaffle.raffle.enterPrice
        return total

    def total_raffels(self):
        return len(self.get_raffels())

    def get_raffles_won(self):
        return len(Raffle.objects.filter(winner=self))

    def get_raffles_wonList(self):
        return Raffle.objects.filter(winner=self).order_by('-endDate')

    def __str__(self):
        return self.email


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="", max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'style': 'margin-bottom: 15px'}))
    password = forms.CharField(label="", max_length=255, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'style': 'margin-bottom: 15px'}))


class UserRegisterForm(forms.Form):
    email = forms.EmailField(label="", max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email', 'style': 'margin-bottom: 15px'}))
    password1 = forms.CharField(label="", max_length=255, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password', 'style': 'margin-bottom: 15px'}))
    password2 = forms.CharField(label="", max_length=255, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Retype Password', 'style': 'margin-bottom: 15px'}))


class Transaction(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey(User)
    time = models.DateTimeField()
    data = models.CharField(max_length=9999, default=None, null=True, blank=True)

    def __str__(self):
        return str(self.id)