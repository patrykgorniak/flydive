from common import HttpManager
from wizzair.commonUrls import CommonData
import re
import json


class WizzairDl(object):

    """Docstring for WizzairDl. """

    def __init__(self):
        """TODO: to be defined1. """
        self.__fetchAirportAndConnections()

    def __fetchAirportAndConnections(self):
        httpcontent = HttpManager.getPage(CommonData.AIRPORTS.value)
        self._airports = self.__getAirports(httpcontent)
        self._connections = self.__getAirportConnections(httpcontent)

    def __getAirports(self, httpContent):
        """Parser HttpContent and return JSON object with airports

        :httpContent: TODO
        :returns: TODO

        """
        airports = re.findall(r'wizzAutocomplete.STATION.*?=\s*(.*?);', httpContent.text, re.DOTALL | re.MULTILINE)
        return json.loads(airports[0], encoding=httpContent.encoding)


    def __getAirportConnections(self, httpContent):
        """Parse HttpContent and return JSON object with fly connections

        :httpContent: TODO
        :returns: TODO

        """
        connections = re.findall(r'wizzAutocomplete.MARKETINFO.*?=\s*(.*?);', httpContent.text, re.DOTALL | re.MULTILINE)
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

