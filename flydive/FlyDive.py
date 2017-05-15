from FLPluginManager import FLPluginManager
from wizzair.wizzairmanager import WizzairPlugin
from ryanair.RyanairManager import RyanairPlugin
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr
from common.NewsletterManager import NewsletterManager
from flight_scheduler.FlightScheduler import FlightScheduler


class FlyDive():
    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.setupLogger(self.cfg['LOGGER'])

        self.flydivePluginManager = FLPluginManager()
        self.flydiveScheduler = FlightScheduler()
        self.newsletterMgr = NewsletterManager()

    def registerPlugins(self):
        if self.cfg['PLUGINS']['wizzair']=='on':
            self.flydivePluginManager.registerPlugin(WizzairPlugin)

        if self.cfg['PLUGINS']['ryanair']=='on':
            self.flydivePluginManager.registerPlugin(RyanairPlugin)

    def setupLogger(self, cfg):
        LogMgr.init(dirname=cfg['config_dir'], configFileName=cfg['config_name'])

    def main(self):

        self.registerPlugins()
        self.flydivePluginManager.initAirports()
        # self.flydivePluginManager.initConnections()

        # newsletter_CfgList = self.newsletterMgr.get()
        # self.flydiveScheduler.dumpToFile("News.txt", newsletter_CfgList)

        # flightTree, connectionList = self.flydiveScheduler.getConnectionsTree(list(newsletter_CfgList.keys()))
        # # Register all FlyDive plugins
        # config = self.flydiveScheduler.getScheduleConfiguration()

        # self.flydivePluginManager.start(flightTree, connectionList, config)
        # scheduledFlights = self.flydiveScheduler.collectFlighDetails(flightTree, config)
        # self.flydiveScheduler.dumpToFile("scheduled.txt", scheduledFlights)

        # filteredFlights = self.flydiveScheduler.removeEmptyFlights(scheduledFlights)
        # self.flydiveScheduler.dumpToFile("filtered.txt", filteredFlights)

        # calculatedFlights = self.flydiveScheduler.calculateCosts(filteredFlights)
        # self.flydiveScheduler.dumpToFile("calculated.txt", calculatedFlights)

        # config = self.flydiveScheduler.getDefaultConfig()

        # filteredFlightPack = self.flydiveScheduler.filterFlightPack(calculatedFlights, newsletter_CfgList)
        # self.flydiveScheduler.dumpToFile("last_step.txt", filteredFlightPack)
        return
