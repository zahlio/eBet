#import urllib.request
#import urllib.parse
import json
from Steam.models import AcceptedItem


class ApiClient(object):
    def __init__(self, key):
        self.key = key #FB2BE1EF8D0E1DE05D5DFDA1A409A13D

    def get_inventory(self, user_id, game_id, category):
        response = json_request(
            "profiles/"
            + user_id
            + "/inventory/json/"
            + game_id
            + "/"
            + category
            + "/?trading=1"
        )

        return Inventory(user_id, response)

    def do_api_call(self, options, page):
        # https://developer.valvesoftware.com/wiki/Steam_Web_API/IEconService
        url = "https://api.steampowered.com/IEconService/" + page +"/v1/?key=" + self.key + "&" + options
        #return urllib.request.urlopen(url)

    # https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key=FB2BE1EF8D0E1DE05D5DFDA1A409A13D&get_received_offers=1&active_only=1


class Inventory(object):
    def __init__(self, user_id, jsonString):
        self.user_id = user_id
        self.items = []

        # rgInventory (list of Item objects)
        # rgDescriptions (list of Desciption objects)
        data = json.loads(jsonString.decode('utf-8'), object_hook=object_decoder)
        temp_items = data['rgInventory']
        temp_descriptions = data['rgDescriptions']
        accepted_items_in_db = AcceptedItem.objects.filter(enabled=True)

        # create the real items list
        for x, desc in temp_descriptions.items():
            for accepted_item in accepted_items_in_db:
                if desc.type == "Base Grade Key" and desc.market_hash_name == accepted_item.market_hash_name and desc.appid == str(accepted_item.appid):
                    for y, item in temp_items.items():
                        if item.classid == desc.classid:
                            item.desc = desc
                            self.items.append(item)

    def total_items(self):
        return len(self.items)


def object_decoder(obj):
    if 'id' in obj and 'classid' in obj:
        return Item(
            obj['id'],
            obj['classid'],
            obj['instanceid'],
            obj['amount'],
            obj['pos'],
            ""
        )
    if 'appid' in obj and 'classid' in obj:
        return Desciption(
            obj['appid'],
            obj['classid'],
            obj['instanceid'],
            obj['icon_url'],
            obj['market_hash_name'],
            obj['tradable'],
            obj['type'],
            obj['marketable']
        )
    return obj


def json_request(url):
    return urllib.request.urlopen("https://steamcommunity.com/" + url).read()


class Item(object):
    def __init__(self, id, classid, instanceid, amount, pos, desc):
        self.id = id
        self.classid = classid
        self.instanceid = instanceid
        self.amount = amount
        self.pos = pos
        self.desc = desc

    def get_image_url(self):
        return "http://steamcommunity-a.akamaihd.net/economy/image/" + self.desc.icon_url


class Desciption(object):
    def __init__(self, appid, classid, instanceid, icon_url, market_hash_name, tradable, type, marketable):
        self.appid = appid
        self.classid = classid
        self.instanceid = instanceid
        self.icon_url = icon_url
        self.market_hash_name = market_hash_name
        self.tradable = tradable
        self.type = type
        self.marketable = marketable
        self.price = 0

    def get_lowest_price(self):

        f = {
            'country': 'DA',
            'currency': '1',
            'appid': self.appid,
            'market_hash_name': self.market_hash_name
        }
        response = json_request(
            "market/priceoverview/?" + urllib.parse.urlencode(f)
        )

        jsondata = json.loads(response.decode('utf-8'))

        if 'lowest_price' in jsondata:
            return float(
                jsondata['lowest_price']
                .replace("&#36;", "")#dollar sign
                .replace(" USD", "")
            )
        return 0