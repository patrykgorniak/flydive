from common import HttpManager
from wizzair.commonUrls import CommonData
from wizzair.commonUrls import TimeTable
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
        self.__updateApiVersion()
        self.__fetchAirportAndConnections()

    def log(self, message=''):
        lm.debug("WizzairDl: {0}".format(message))

    def __updateApiVersion(self):
        content = HttpManager.getMethod(CommonData.MAIN).text
        api_version = re.findall(r'var apiUrl =\s*(.*?);', content, re.DOTALL | re.MULTILINE)[0].replace('"','')
        CommonData.Search = CommonData.Search.format(api_version)
        self.log("Search api: {}".format(CommonData.Search))
        return api_version


    def getTimeTable(self, details = { "src_iata": "", "dst_iata":"", "year":"", "month":"" }):
        """ Downloads monthly timetable for connection details
        :details: connection details with src_iata, dst_iata, year and month 
        :returns: content in json format from service
        """
        src_iata = details['src_iata']
        dst_iata = details['dst_iata']
        year = details['year']
        month = details['month']

        url = CommonData.TimeTable
        url = url.format(src_iata, dst_iata, year, month)

        filePath = os.path.join(self.base, '{0}_{1}_{2}_{3}.json'.format(src_iata, dst_iata, month, year))

        if self.cfg['DEBUGGING']['state'] == 'online':
            self.log("Get from: " + url)
            httpContent = HttpManager.getMethod(url).text
            self.writeToFile(filePath, httpContent)
        else:
            self.log("Get from: " + filePath)
            with open(filePath, 'r') as f:
                httpContent = f.read()
            f.close()

        return json.loads(httpContent)

    def __fetchAirportAndConnections(self):
        self.log("fetchAirportAndConnections")

        if self.cfg['DEBUGGING']['state'] == 'online':
            httpcontent = HttpManager.getMethod(CommonData.AIRPORTS).text
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

    def packParamsToJSON(self, flight):

        if type(flight) is not TimeTable:
            raise TypeError('flight is not a TimeTable type')

        params = {
            'adultCount': 1,
            'infantCount': 0,
            'childCount': 0,
            'wdc': 1,
            'flightList': [
                {
                    'departureStation': flight.src,
                    'arrivalStation': flight.dst,
                    'departureDate': flight.date.strftime("%Y-%m-%d")
                },
                {
                    'departureStation': flight.dst,
                    'arrivalStation': flight.src,
                    'departureDate': flight.date.strftime("%Y-%m-%d")
                }
            ]
        }
        return params

    def getFlightDetails(self, flight):
        """TODO: Docstring for __searchFlight.

        :options: TODO
        : {'src_iata':'': TODO
        :'dst_iata':'': TODO
        :'date':''}: TODO
        :returns: TODO

        """
        if type(flight) is not TimeTable:
            raise TypeError('flight is not a TimeTable type')

        params = self.packParamsToJSON(flight)

        filePath = os.path.join(self.base, '{0}_{1}_{2}.json'.format(flight.src, flight.dst, flight.date))
        if self.cfg['DEBUGGING']['state'] == 'online':
            httpContent = HttpManager.postMethod(CommonData.Search, params).text
            self.writeToFile(filePath, httpContent)
        else:
            filePath = os.path.join(self.base, '{0}_{1}_{2}.json'.format(flight.src, flight.dst, flight.date))
            self.log("Get from: " + filePath)
            with open(filePath, 'r') as f:
                httpContent = f.read()
            f.close()

        return json.loads(httpContent)

    def writeToFile(self, filePath, httpContent):
        """TODO: Docstring for writeToFile.

        :filepath: TODO
        :data: TODO
        :returns: TODO

        """
        self.log("Write to: " + filePath)
        with open(filePath, 'w') as f:
            f.write(httpContent)
        f.close()

