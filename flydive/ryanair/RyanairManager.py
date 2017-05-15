from FLEngineCreator import FLEngineCreator
from ryanair.RyanairDl import RyanairDl
from ryanair.RyanairParser import RyanairParser
from ryanair import RyanairUrls as RyanairData
from common.SessionManager import SessionManager

class RyanairPlugin(FLEngineCreator):
    def __init__(self, _db, _cfg, asyncDlMgr = None):
        FLEngineCreator.__init__(self, _cfg, RyanairParser(), RyanairDl(), RyanairData, _db,
                                 SessionManager(RyanairData.airline_name), asyncDlMgr)

    def initAirports(self):
        FLEngineCreator.initAirports(self)

    def initConnections(self):
        FLEngineCreator.initConnections(self)

    def run(self, flightTree, connectionList, config):
        FLEngineCreator.run(self, flightTree, connectionList, config)
