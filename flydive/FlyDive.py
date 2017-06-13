import argparse
from FLPluginManager import FLPluginManager
from wizzair.wizzairmanager import WizzairPlugin
from ryanair.RyanairManager import RyanairPlugin
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr
from common.NewsletterManager import NewsletterManager
from flight_scheduler.FlightScheduler import FlightScheduler

class FlyDive():
    def __init__(self):
        self.args = self.initArgParser()
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

    def initArgParser(self):
        parser = argparse.ArgumentParser(description="Flydive - help")
        parser.add_argument('-s', '--schedule', action='store_true', help='Run scheduler')
        # parser.add_argument('-c','--connections', action='store_true', help='Update connections')
        # parser.add_argument('-d', '--fetchdetails', action='store_true', help='Init airports')
        # parser.add_argument('-s', '--schedule', action='store_true', help='Init airports')
        args = parser.parse_args()
        return args

    def main(self):
        self.registerPlugins()

        if not self.args.schedule:
            self.flydivePluginManager.initAirports()
            self.flydivePluginManager.initConnections()

        # if self.args.fetchdetails:
        newsletter_CfgList = self.newsletterMgr.get()
        newsletter_CfgList2 = self.newsletterMgr.unpack()
        self.flydiveScheduler.dumpToFile("Newsletter_CfgList2.txt", newsletter_CfgList2)

        flightTree, connectionList = self.flydiveScheduler.getConnectionsTree([ x for y in newsletter_CfgList2 for x in list(y.keys())]) #list(newsletter_CfgList.keys()))
        # # Register all FlyDive plugins
        config = self.flydiveScheduler.getScheduleConfiguration(newsletter_CfgList2)

        if not self.args.schedule:
            self.flydivePluginManager.start(flightTree, connectionList, config)
        
        scheduledFlights = self.flydiveScheduler.collectFlighDetails(flightTree, config)
        self.flydiveScheduler.dumpToFile("collectFlighDetails.txt", scheduledFlights)
        scheduledFlights2 = self.flydiveScheduler.collectFlighDetails2(flightTree, config, newsletter_CfgList2)
        self.flydiveScheduler.dumpToFile("collectFlighDetails2.txt", scheduledFlights2)

        # filteredFlights = self.flydiveScheduler.removeEmptyFlights(scheduledFlights2)
        # self.flydiveScheduler.dumpToFile("removeEmptyFlights.txt", filteredFlights)

        calculatedFlights = self.flydiveScheduler.calculateCosts(scheduledFlights2)
        self.flydiveScheduler.dumpToFile("calculateCosts.txt", calculatedFlights)

        # filteredFlightPack = self.flydiveScheduler.filterFlightPack(calculatedFlights, newsletter_CfgList)
        # self.flydiveScheduler.dumpToFile("newsletter.txt", filteredFlightPack)
        return
