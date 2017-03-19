from common import LogManager as lm
from common.FLPlugin import FLPlugin
from common import DownloadManager

class FLPluginManager(object):

    def __init__(self):
        self.plugins = []
        self.asyncDlMgr =  DownloadManager.AsyncDownloadManager()

    def log(self, message):
        lm.debug("FLPluginManager: {0}".format(message))

    def registerPlugin(self, FLPluginType):
        plugin = FLPluginType(self.asyncDlMgr)
        assert(isinstance(plugin, FLPlugin), "{} is not type of FLPlugin.".format(plugin))

        lm.debug("New plugin registered: {}".format(FLPluginType))
        self.plugins.append(plugin)

    def start(self):
        for plugin in self.plugins:
            plugin.run()
