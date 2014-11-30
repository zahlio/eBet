from django.db import models


class LoginLog(models.Model):
    date = models.DateTimeField()
    user = models.ForeignKey('Accounting.User')
    ip = models.CharField(max_length=255)

    def __str__(self):
        return "(" + self.user.email + ") " + str(self.date) + " - " + str(self.ip)


class BetSettleLog(models.Model):
    date = models.DateTimeField()
    bet = models.ForeignKey('Bet.GameBet')
    ourCut = models.FloatField()

    def __str__(self):
        return str(self.date) + " - " + str(self.bet.__str__())


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip