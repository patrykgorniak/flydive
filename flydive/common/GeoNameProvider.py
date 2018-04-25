import re
import json
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
from common import HttpManager
import common.CurrencyProvider as CurrencyProvider

class GeoNameProvider():
    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.user = self.cfg["GEO_NAME_PROVIDER"]["user"]
        self.url_base = "http://ws.geonames.org/countryCodeJSON?lat={}&lng={}&radius=60&username={}"
        self.url_base2 = "http://api.geonames.org/searchJSON?name={}&username={}"
        self.currencyProvider = CurrencyProvider.getCurrencyProvider()

    def log(self, message=''):
        lm.debug("GeoNameProvider: {0}".format(message))

    def getGeoData(self, airport): #geo_position = {"lat": 0, "long": 0, "name": "" }):
        lat = airport.latitude #geo_position['lat']
        long = airport.longitude #geo_position['long']
        name = airport.name #geo_position['name']

        if lat is None or long is None:
            name = re.sub(r' \(.*\)','',name)
            url = self.url_base2.format(name, self.user)
            json_data = self.searchByName(url)
            airport.latitude = json_data['lat'] if 'lat' in json_data else None
            airport.longitude = json_data['lng'] if 'lng' in json_data else None
        else:
            url = self.url_base.format(lat, long, self.user)
            json_data = self.searchByGeo(url)
        
        self.log("REQ: {} \nRESP: {} ".format(url, json_data))

        currency = self.getCurrencyInfo(json_data['countryName'])
        json_data['currencyCode'] = currency.currencyCode
        json_data['currencyName'] = currency.currencyName
        json_data['currencyNumber'] = currency.currencyNumber

        airport.country_name    = json_data['countryName']
        airport.country_code    = json_data['countryCode']
        airport.currency_code   = json_data['currencyCode']
        airport.currency_name   = json_data['currencyName']
        airport.currency_number = json_data['currencyNumber']
        
        return airport

    def searchByGeo(self, url):
        resp = HttpManager.getMethod(url).text
        json_data = json.loads(resp)
        return json_data

    def searchByName(self, url):
        resp = HttpManager.getMethod(url).text
        json_data = json.loads(resp)
        if int(json_data['totalResultsCount']) > 0:
            return json_data['geonames'][0]
        else:
            return {'countryCode':"N/A", "countryName": "N/A"}

    def getCurrencyInfo(self, country):
        return self.currencyProvider.getCurrency(country)

