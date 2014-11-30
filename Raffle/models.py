from datetime import datetime
from django.db import models
from django.template.defaultfilters import register

class Price(models.Model):
    realPrice = models.FloatField()
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='static/uploads/', help_text='Should be 800x300')
    desc = models.TextField(help_text="Please enter this in HTML")

    def get_small_desc(self):
        return self.desc[:25] + "..."

    def __str__(self):
        return self.name


class Raffle(models.Model):
    startDate = models.DateTimeField()
    endDate = models.DateTimeField(default=None, null=True, blank=True)
    winner = models.ForeignKey('Accounting.User', default=None, null=True, blank=True)
    enterPrice = models.FloatField()
    price = models.ForeignKey(Price)
    game = models.ForeignKey('Accounting.Game')
    maxEnterTimes = models.IntegerField()
    slots = models.IntegerField()

    def __str__(self):
        return str(self.id)

    def slots_left(self):
        return self.slots - len(RaffleEntry.objects.filter(raffle=self))

    def get_slots_used(self):
        return len(RaffleEntry.objects.filter(raffle=self))

    def get_users_in(self):
        return RaffleEntry.objects.filter(raffle=self).order_by('-date')

    @register.filter
    def get_user_entries(self, user):
        return len(RaffleEntry.objects.filter(raffle=self, user=user))

    def enter(self, user):
        if user.get_balance() < self.enterPrice:
            return False
        if self.get_user_entries(user) >= self.maxEnterTimes:
            return False
        if self.winner is not None or self.endDate is not None:
            return False
        if self.slots <= self.get_slots_used():
            return False

        transaction = user.create_transaction(-self.enterPrice, "Payment for raffle: <a href='/raffle/" + str(self.id) + "/'>#" + str(self.id) + "</a>")

        # if we made it this far, then we join
        user_raffle = RaffleEntry(
            user=user,
            raffle=self,
            date=datetime.now(),
            transaction=transaction
        )
        user_raffle.save()

        if self.slots <= self.get_slots_used():
            self.end()

        return True

    def end(self):
        self.endDate = datetime.now()
        self.winner = RaffleEntry.objects.filter(raffle=self).order_by('?')[0].user
        self.save()


class RaffleEntry(models.Model):
    user = models.ForeignKey('Accounting.User')
    raffle = models.ForeignKey(Raffle)
    date = models.DateTimeField()
    transaction = models.ForeignKey('Accounting.Transaction')

    def __str__(self):
        return str(self.id)

    def time_since_html(self):
        delta = datetime.now().replace(tzinfo=None) - self.date.replace(tzinfo=None)

        hours = int(delta.seconds / 60 / 60)
        minutes = int(delta.seconds / 60)
        if delta.days >= 1:
            return "Joined {0} days ago".format(delta.days)
        elif hours >= 1:
            return "Joined {0} hours ago".format(hours)
        elif minutes >= 1:
            return "Joined {0} minutes ago".format(minutes)
        else:
            return "Joined {0} seconds ago".format(delta.seconds)


@register.filter
def procent(value, arg):
    '''
    Divides the value; argument is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = int(value)
        arg = int(arg)
        if arg: return (value / arg) * 100
    except: pass
    return 0
