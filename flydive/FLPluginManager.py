from common import LogManager as lm
from common.FLPlugin import FLPlugin
from common import DownloadManager
from common.ConfigurationManager import CfgMgr
from common.DatabaseManager import DatabaseManager
from FLEngineCreator import FLEngineCreator

class FLPluginManager(object):

    def __init__(self):
        self.plugins = []
        self.asyncDlMgr =  DownloadManager.AsyncDownloadManager()
        self.cfg = CfgMgr().getConfig()
        # READ CONFIG DATA
        self.db = DatabaseManager(self.cfg['DATABASE']['name'],
                                  self.cfg['DATABASE']['type'],
                                  self.cfg['DATABASE']['server'],
                                  self.cfg['DATABASE']['pass'],
                                  self.cfg['DATABASE']['user'] )

    def log(self, message):
        lm.debug("FLPluginManager: {0}".format(message))

    def registerPlugin(self, FLPluginType):
        plugin = FLPluginType(self.db, self.cfg, self.asyncDlMgr)
        assert isinstance(plugin, FLEngineCreator), "{} is not type of FLEngineCreator.".format(plugin)

        lm.debug("New plugin registered: {}".format(FLPluginType))
        self.plugins.append(plugin)

    def initConnections(self):
        for plugin in self.plugins:
            plugin.initConnections()

    def initAirports(self):
        for plugin in self.plugins:
            plugin.initAirports()

    def start(self, flightTree, connectionList, config):
        # TODO: change to parallel, use threads
        for plugin in self.plugins:
            plugin.run(flightTree, connectionList, config)
