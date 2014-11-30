from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.shortcuts import render_to_response
from Steam.apiClient import *
from Steam.models import *
from Raffle.models import *
from Bet.models import *
from Accounting.models import *
from Logging.models import *


def index(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])
    return render(request, 'index.html', {
        'frontPageItems': GameBet.objects.filter(winner=None).order_by('?')[:3],
        'betList': GameBet.objects.filter(winner=None).order_by('-bet_end')[:3],
        'raffleList': Raffle.objects.filter(endDate=None).order_by('-startDate')[:3],
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def raffle(request, Raffle_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, 'raffle.html', {
        'raffle': get_object_or_404(Raffle, id=Raffle_id),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def enter(request, Raffle_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, 'enter.html', {
        'raffle': get_object_or_404(Raffle, id=Raffle_id),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def login(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=request.POST['email'])
            except User.DoesNotExist:
                user = 0
            if user is not 0:
                if user.banned:
                    return render(request, 'login.html', {
                        'form': form,
                        'error': "Account is banned",
                        'user': user,
                        'gamesList': Game.objects.filter().order_by('name')
                    })
                else:
                    if user.pwd == request.POST['password']:
                        request.session['user_id'] = user.id
                        # log
                        l = LoginLog(
                            user=user,
                            date=datetime.now(),
                            ip=get_client_ip(request),
                        )
                        l.save()
                        return redirect(index)
                    else:
                        return render(request, 'login.html', {
                            'form': form,
                            'error': "Wrong password",
                            'user': user,
                            'gamesList': Game.objects.filter().order_by('name')
                        })
            else:
                return render(request, 'login.html', {
                    'form': form,
                    'error': "Email does not exist.",
                    'user': user,
                    'gamesList': Game.objects.filter().order_by('name')
                })
        else:
            return render(request, 'login.html', {
                'form': form,
                'error': "There was an error",
                'user': user,
                'gamesList': Game.objects.filter().order_by('name')
            })
    else:
        form = UserLoginForm()
        return render(request, 'login.html', {
            'form': form,
            'user': user,
            'gamesList': Game.objects.filter().order_by('name')
        })


def logout(request):
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return redirect('/login/')


def register(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            if request.POST['password1'] == request.POST['password2']:
                # register the user

                try:
                    old_user = User.objects.get(email=request.POST['email'])
                except User.DoesNotExist:
                    old_user = None

                if old_user is None:
                    # we create a new user
                    new_user = User(
                        password=request.POST['password1'],
                        email=request.POST['email']
                    )
                    new_user.save()
                    request.session['user_id'] = new_user.id
                    return redirect('/')
                else:
                    return render(request, 'register.html', {
                        'form': form,
                        'error': "That email already exists in our system",
                        'user': user,
                        'gamesList': Game.objects.filter().order_by('name')
                    })
            else:
                return render(request, 'register.html', {
                    'form': form,
                    'error': "Please type in the same password twice",
                    'user': user,
                    'gamesList': Game.objects.filter().order_by('name')
                })
        else:
            return render(request, 'register.html', {
                'form': form,
                'error': "There was an error",
                'user': user,
                'gamesList': Game.objects.filter().order_by('name')
            })
    else:
        form = UserRegisterForm()
        return render(request, 'register.html', {
            'form': form,
            'user': user,
            'gamesList': Game.objects.filter().order_by('name')
        })


def raffles(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])
    return render(request, 'raffles.html', {
        'frontPageItems': Raffle.objects.filter(endDate=None).order_by('-startDate'),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def rafflesGame(request, Game_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])
    return render(request, 'raffles.html', {
        'frontPageItems': Raffle.objects.filter(endDate=None, game=Game_id).order_by('-startDate'),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def submit(request, Raffle_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    if request.method == 'POST':
        raffle = get_object_or_404(Raffle, id=Raffle_id)

        if raffle.enter(user):
            msg = "You have successfully been added to the raffle"
        else:
            msg = "There was an error with your request, please try again."

        return render(request, 'submit.html', {
            'msg': msg,
            'raffle': raffle,
            'user': user,
            'gamesList': Game.objects.filter().order_by('name')
        })
    else:
        raise Http404


def wallet(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, 'wallet.html', {
        'transactionsList': Transaction.objects.filter(user=user).order_by('-time'),
        'user': user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def account(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        user = 0
    else:
        user = get_object_or_404(User, id=request.session['user_id'])

        return render(request, 'account.html', {
            'user': user,
            'gamesList': Game.objects.filter().order_by('name')
        })


def trade(request):

    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        our_user = 0
    else:
        our_user = get_object_or_404(User, id=request.session['user_id'])

    client = ApiClient("FB2BE1EF8D0E1DE05D5DFDA1A409A13D")
    inventory = client.get_inventory("76561197984683709", "730", "2")

    # we create the Trade
    tradeObj = Trade(
        user=our_user,
        start=datetime.now(),
        isComplete=False
    )
    tradeObj.save()

    return render(request, 'trade.html', {
        'trade': tradeObj,
        'acceptedItems': AcceptedItem.objects.filter(enabled=True),
        'inventory': inventory,
        'user': our_user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def trade_overview(request, Trade_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        our_user = 0
    else:
        our_user = get_object_or_404(User, id=request.session['user_id'])

    trade_obj = get_object_or_404(Trade, id=Trade_id)

    if request.method == 'POST' and trade_obj.items_count() == 0:
        client = ApiClient("000")
        inventory = client.get_inventory("76561197984683709", "730", "2")
        trade_items = request.POST.getlist('item')

        #we add the items to the trade
        for trade_item in trade_items:
            for inventoryItem in inventory.items:
                if trade_item == inventoryItem.classid:
                    accepted_item = get_object_or_404(AcceptedItem, market_hash_name=inventoryItem.desc.market_hash_name)
                    new_trade_item = TradeItem(trade=trade_obj, item=accepted_item, price=inventoryItem.desc.get_lowest_price(), priceDate=datetime.now() )
                    new_trade_item.save()
                    break

    return render(request, 'trade_overview.html', {
        'trade': trade_obj,
        'tradeItems': TradeItem.objects.filter(trade=trade_obj),
        'user': our_user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def trade_offer(request, Trade_id):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        return redirect('/login/')
        our_user = 0
    else:
        our_user = get_object_or_404(User, id=request.session['user_id'])

    trade_obj = get_object_or_404(Trade, id=Trade_id)

    return render(request, 'trade_offer.html', {
        'trade': trade_obj,
        'tradeItems': TradeItem.objects.filter(trade=trade_obj),
        'user': our_user,
        'gamesList': Game.objects.filter().order_by('name')
    })


def error404(request):
    user_id = request.session.get('user_id', None)
    if user_id is None:
        our_user = 0
    else:
        our_user = get_object_or_404(User, id=request.session['user_id'])

    return render(request, '404.html', {
        'user': our_user,
        'gamesList': Game.objects.filter().order_by('name')
    })