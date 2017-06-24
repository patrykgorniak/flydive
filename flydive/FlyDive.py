import argparse
from FLPluginManager import FLPluginManager
from newsletter.FLNewsletter import FLNewsletter
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
        self.newsletter = FLNewsletter()

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
        # newsletter_CfgList = self.newsletterMgr.get()
        newsletter_CfgList = self.newsletterMgr.unpack()
        self.flydiveScheduler.dumpToFile("Newsletter_CfgList.txt", newsletter_CfgList)

        flightTree, connectionList = self.flydiveScheduler.getConnectionsTree([ x for y in newsletter_CfgList for x in list(y.keys())]) #list(newsletter_CfgList.keys()))
        # # Register all FlyDive plugins
        config = self.flydiveScheduler.getScheduleConfiguration(newsletter_CfgList)

        if not self.args.schedule:
            self.flydivePluginManager.start(flightTree, connectionList, config)

        scheduledFlights = self.flydiveScheduler.collectFlighDetails2(flightTree, config, newsletter_CfgList)
        self.flydiveScheduler.dumpToFile("collectFlighDetails.txt", scheduledFlights)

        filteredFlightPack = self.flydiveScheduler.filterFlightPack2(scheduledFlights, newsletter_CfgList)
        self.flydiveScheduler.dumpToFile("filteredFlightPack.txt", filteredFlightPack)

        calculatedFlights = self.flydiveScheduler.calculateCosts(filteredFlightPack)
        self.flydiveScheduler.dumpToFile("calculateCosts.txt", calculatedFlights)

        self.newsletter.prepare_HTML(calculatedFlights)
        return
