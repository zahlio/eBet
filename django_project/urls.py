from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'django_project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', 'Raffle.views.index'),

    # raffles lists
    url(r'^raffles/$', 'Raffle.views.raffles'),
    url(r'^raffles/(?P<Game_id>\d+)/$', 'Raffle.views.rafflesGame'),

    # single raffle
    url(r'^raffle/(?P<Raffle_id>\d+)/$', 'Raffle.views.raffle'),
    url(r'^raffle/(?P<Raffle_id>\d+)/enter/$', 'Raffle.views.enter'),
    url(r'^raffle/(?P<Raffle_id>\d+)/enter/submit/$', 'Raffle.views.submit'),

    # Bets list
    url(r'^bets/$', 'Bet.views.bets'),
    url(r'^bets/(?P<Game_id>\d+)/$', 'Bet.views.betsGame'),

    # single bet
    url(r'^bet/(?P<Bet_id>\d+)/$', 'Bet.views.bet'),
    url(r'^bet/(?P<Bet_id>\d+)/enter/$', 'Bet.views.enter'),
    url(r'^bet/(?P<Bet_id>\d+)/enter/submit/$', 'Bet.views.submit'),

    # account
    url(r'^account/$', 'Raffle.views.account'),
    url(r'^wallet/$', 'Raffle.views.wallet'),

    # trade
    url(r'^trade/$', 'Raffle.views.trade'),
    url(r'^trade/(?P<Trade_id>\d+)/$', 'Raffle.views.trade_overview'),
    url(r'^trade/(?P<Trade_id>\d+)/offer/$', 'Raffle.views.trade_offer'),

    # account modifiers
    url(r'^login/', 'Raffle.views.login'),
    url(r'^logout/', 'Raffle.views.logout'),
    url(r'^register/', 'Raffle.views.register'),
)

admin.site.site_header = 'eBet - Administrator'
admin.site.site_title = 'eBet - Administrator'
admin.site.index_title = "Backend"

handler404 = 'Raffle.views.error404'
