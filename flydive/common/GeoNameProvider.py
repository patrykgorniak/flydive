import re
import json
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
from common import HttpManager

class GeoNameProvider():
    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.user = self.cfg["GEO_NAME_PROVIDER"]["user"]
        self.url_base = "http://ws.geonames.org/countryCodeJSON?lat={}&lng={}&radius=60&username={}"
        self.url_base2 = "http://api.geonames.org/searchJSON?name={}&username={}"

    def log(self, message=''):
        lm.debug("GeoNameProvider: {0}".format(message))

    def getGeoName(self, geo_position = {"lat": 0, "long": 0, "name": "" }):
        lat = geo_position['lat']
        long = geo_position['long']
        name = geo_position['name']

        if lat is None or long is None:
            name = re.sub(r' \(.*\)','',name)
            url = self.url_base2.format(name, self.user)
            json_data = self.searchByName(url)
        else:
            url = self.url_base.format(lat, long, self.user)
            json_data = self.searchByGeo(url)
        
        self.log("REQ: {} \nRESP: {} ".format(url, json_data))
        return json_data

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



