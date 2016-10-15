from common import HttpManager
from wizzair.commonUrls import CommonData
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
import re
import json
import os


class WizzairDl(object):

    """Docstring for WizzairDl. """
    def __init__(self):
        """TODO: to be defined1. """
        self.cfg = CfgMgr().getConfig()
        self.base = os.path.join(os.path.dirname(os.path.realpath(__file__)),'../../tests/wizzair/testdata/')
        self.__fetchAirportAndConnections()

    def log(self, message=''):
        lm.debug("WizzairDl: {0}".format(message))

    def fetchFlightDetails(self, details = { "src_iata": "", "dst_iata":"", "year":"", "month":"" }):
        src_iata = details['src_iata']
        dst_iata = details['dst_iata']
        year = details['year']
        month = details['month']

        url = CommonData.TimeTable.value
        url = url.format(src_iata, dst_iata, year, month)
        lm.debug(url)

        if self.cfg['DEBUGGING']['state'] == 'online':
            httpContent = HttpManager.getMethod(url)
        else:
            filePath = os.path.join(self.base, '{0}_{1}_{2}_{3}.json'.format(src_iata, dst_iata, month, year))
            with open(filePath, 'r') as f:
                httpContent = f.read()
            f.close()

        return json.loads(httpContent)

    def __fetchAirportAndConnections(self):
        self.log("fetchAirportAndConnections")

        if self.cfg['DEBUGGING']['state'] == 'online':
            httpcontent = HttpManager.getMethod(CommonData.AIRPORTS.value).text
        else:
            filePath = os.path.join(self.base, 'Markets.json')
            with open(filePath, 'r') as f:
                httpcontent = f.read()
            f.close()

        self._airports = self.__getAirports(httpcontent)
        self._connections = self.__getAirportConnections(httpcontent)

    def __getAirports(self, httpContent):
        """Parser HttpContent and return JSON object with airports

        :httpContent: TODO
        :returns: TODO

        """
        airports = re.findall(r'wizzAutocomplete.STATION.*?=\s*(.*?);', httpContent, re.DOTALL | re.MULTILINE)
        # return json.loads(airports[0], encoding=httpContent.encoding)
        return json.loads(airports[0])


    def __getAirportConnections(self, httpContent):
        """Parse HttpContent and return JSON object with fly connections

        :httpContent: TODO
        :returns: TODO

        """
        connections = re.findall(r'wizzAutocomplete.MARKETINFO.*?=\s*(.*?);', httpContent, re.DOTALL | re.MULTILINE)
        return json.loads(connections[0].replace("'",""))

    def getAirports(self, pattern=''):
        """TODO: Docstring for getAirports.

        :pattern: TODO
        :returns: TODO

        """
        return self._airports;

    def getConnections(self, pattern=''):
        """TODO: Docstring for getConnections.

        :pattern: TODO
        :returns: TODO

        """
        return self._connections;

    def __searchFlight(self, options={'src_iata':'WAW', 'dst_iata':'LTN', 'date':'2016-10-21'}):
        """TODO: Docstring for __searchFlight.

        :options: TODO
        :'dst_iata':'': TODO
        :'date':''}: TODO
        :returns: TODO

        """
        params = {
            'adultCount': 1,
            'infantCount': 0,
            'childCount': 0,
            'wdc': 1,
            'flightList': [
                {
                    'arrivalStation': options['dst_iata'],
                    'departureStation': options['src_iata'],
                    'departureDate': options['date']
                }
            ]
        }

        httpContent = HttpManager.postMethod(CommonData.Search.value, params)

