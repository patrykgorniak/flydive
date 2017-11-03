from common.SessionManager import SessionManager
from FLEngineCreator import FLEngineCreator

from wizzair.wizzairdl import WizzairDl
from wizzair.WizzairParser import WizzairParser
from wizzair import commonUrls as WizzData


class WizzairPlugin(FLEngineCreator):
    def __init__(self, _db, _cfg, asyncDlMgr = None):
        self.use_post = True
        FLEngineCreator.__init__(self, _cfg, WizzairParser(), WizzairDl(), WizzData, _db,
                                 SessionManager(WizzData.airline_name), self.use_post, asyncDlMgr)

    def initAirports(self):
        FLEngineCreator.initAirports(self)

    def initConnections(self):
        FLEngineCreator.initConnections(self)

    def run(self, flightTree, connectionList, config):
        FLEngineCreator.run(self, flightTree, connectionList, config)

    def getAirlineCode(self):
        return WizzData.carrierCode

