from django.db import models
# Create your models here.


class AcceptedItem(models.Model):
    market_hash_name = models.CharField(max_length=255)
    appid = models.IntegerField()
    enabled = models.BooleanField(default=True)


class TradeOffer(models.Model):
    # https://steamcommunity.com/tradeoffer/new/?partner=84196921&token=2Ayk7w3o
    tradeofferid = models.CharField(max_length=255)


class Trade(models.Model):
    user = models.ForeignKey('Accounting.User')
    start = models.DateTimeField()
    offer = models.ForeignKey(TradeOffer, blank=True, null=True)
    isComplete = models.BooleanField(default=False)

    def get_amount(self):
        amount = 0
        for item in TradeItem.objects.filter(trade=self):
            amount = item.price + amount

        return round(amount, 2)

    def items_count(self):
        return len(TradeItem.objects.filter(trade=self))

    def fee(self):
        #10%
        return round((self.get_amount() / 100) * 10, 2)

    def payable_amount(self):
        return round(self.get_amount() - self.fee(), 2)

    def create_trade_offer(self):
        offer = TradeOffer()


class TradeItem(models.Model):
    trade = models.ForeignKey(Trade)
    item = models.ForeignKey(AcceptedItem)
    price = models.FloatField()
    priceDate = models.DateTimeField()