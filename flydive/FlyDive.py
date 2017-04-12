from FLPluginManager import FLPluginManager
from wizzair.wizzairmanager import WizzairPlugin
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr
from flight_scheduler.FlightScheduler import FlightScheduler


class FlyDive():
    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.setupLogger(self.cfg['LOGGER'])

        self.flydivePluginManager = FLPluginManager()
        self.flydiveScheduler = FlightScheduler()

    def registerPlugins(self):
        self.flydivePluginManager.registerPlugin(WizzairPlugin)

    def setupLogger(self, cfg):
        LogMgr.init(dirname=cfg['config_dir'], configFileName=cfg['config_name'])

    def main(self):
        self.registerPlugins()
        self.flydivePluginManager.initAirports()
        self.flydivePluginManager.initConnections()

        flightTree, connectionList = self.flydiveScheduler.getConnectionsTree()
        # Register all FlyDive plugins
        config = self.flydiveScheduler.getScheduleConfiguration()
        self.flydivePluginManager.start(flightTree, connectionList, config)
        self.flydiveScheduler.collectFlighDetails(flightTree, config)
        return

