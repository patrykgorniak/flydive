from interfaces.DownloadIface import DownloadIface
from common.ConfigurationManager import CfgMgr
from common import HttpManager 
import json

from plugins.norwegian.Common import CommonData
from _ast import For

class NorwegianDownloader(DownloadIface):
    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.__fetchAirportAndConnections()

    def __fetchAirportAndConnections(self):
        httpcontent = HttpManager.getMethod(CommonData.AIRPORTS).text
        json_data = json.loads(httpcontent)

        self._airports = json_data['destinations']
        self._connections = self.__checkConnectionsConsistency(self._airports, json_data['relations'])

    def getAirports(self, pattern=''):
        return self._airports;

    def getConnections(self, pattern=''):
        return self._connections
    
    def __checkConnectionsConsistency(self, airports, connections):
        airportList = self.__buildAirportList(airports)
        consistent_connections = {}
        
        for departure in connections.keys():
            if departure.upper() in airportList:
                consistent_connections[departure.upper()] = [ x for x in connections[departure] if x in airportList] 
                
        return consistent_connections
    
    def __buildAirportList(self, airports_json):
        return [x['cityCode'] for x in airports_json if x['cityCode'][-3:] != "ALL"]
                