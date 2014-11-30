from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.shortcuts import render_to_response
from Steam.apiClient import *
from Steam.models import *
from Raffle.models import *
from Bet.models import *
from Accounting.models import *


def bet(request, Bet_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, 'bet.html', {
        'bet': get_object_or_404(GameBet, id=Bet_id),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def bets(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])
    return render(request, 'bets.html', {
        'frontPageItems': GameBet.objects.filter(winner=None).order_by('-bet_end'),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def betsGame(request, Game_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])
    return render(request, 'bets.html', {
        'frontPageItems': GameBet.objects.filter(winner=None, game=Game_id).order_by('-bet_end'),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def enter(request, Bet_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, 'bet_enter.html', {
        'bet': get_object_or_404(GameBet, id=Bet_id),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def submit(request, Bet_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        bet = get_object_or_404(GameBet, id=Bet_id)
        amount = float(request.POST['amount'])
        raw_team = request.POST['team']

        team = None

        if raw_team == "team1":
            team = bet.team1
        else:
            team = bet.team2

        if bet.enter_bet(team, amount, user):
            msg = "You have successfully entered the bet with a total of $" + str(amount) + " on " + team.name
        else:
            msg = "There was an error with your request, please try again."

        return render(request, 'bet_submit.html', {
            'msg': msg,
            'bet': bet,
            'user': user,
            'gamesList': Game.objects.filter().order_by('name')
        })
    else:
        raise Http404