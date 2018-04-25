
from common.SessionManager import SessionManager
from FLEngineCreator import FLEngineCreator

from plugins.norwegian.Downloader import NorwegianDownloader
from plugins.norwegian.Parser import NorwegianParser
from plugins.norwegian import Common as CommonData


class NorwegianPlugin(FLEngineCreator):
    def __init__(self, _db, _cfg, asyncDlMgr = None):
        self.use_post = True
        FLEngineCreator.__init__(self, _cfg, NorwegianParser(), NorwegianDownloader(), CommonData, _db,
                                 SessionManager(CommonData.airline_name), self.use_post, asyncDlMgr)

    def initAirports(self):
        FLEngineCreator.initAirports(self)

    def initConnections(self):
        FLEngineCreator.initConnections(self)

    def run(self, flightTree, connectionList, config):
        FLEngineCreator.run(self, flightTree, connectionList, config)

    def getAirlineCode(self):
        return CommonData.carrierCode

