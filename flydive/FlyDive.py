import argparse
from FLPluginManager import FLPluginManager
from newsletter.FLNewsletter import FLNewsletter
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr
from common.NewsletterManager import NewsletterManager
from flight_scheduler.FlightScheduler import FlightScheduler

from plugins.wizzair.wizzairmanager import WizzairPlugin
from plugins.ryanair.RyanairManager import RyanairPlugin
from plugins.norwegian.Manager import NorwegianPlugin

class FlyDive():
    def __init__(self):
        self.args = self.initArgParser()
        self.cfg = CfgMgr().getConfig()
        self.setupLogger(self.cfg['LOGGER'], self.args.debug)

        self.flydivePluginManager = FLPluginManager()
        self.flydiveScheduler = FlightScheduler()
        self.newsletterMgr = NewsletterManager(self.args.config)
        self.newsletter = FLNewsletter()
        self.enabled_airlines = []

    def registerPlugins(self):
        if self.cfg['PLUGINS']['wizzair']=='on':
            self.enabled_airlines.append(self.flydivePluginManager.registerPlugin(WizzairPlugin))

        if self.cfg['PLUGINS']['ryanair']=='on':
            self.enabled_airlines.append(self.flydivePluginManager.registerPlugin(RyanairPlugin))

        if self.cfg['PLUGINS']['norwegian']=='on':
            self.enabled_airlines.append(self.flydivePluginManager.registerPlugin(NorwegianPlugin))

    def setupLogger(self, cfg, dump_files):
        LogMgr.init(dump_files, dirname=cfg['config_dir'], configFileName=cfg['config_name'])

    def initArgParser(self):
        parser = argparse.ArgumentParser(description="Flydive - help")
        parser.add_argument('-r', '--refresh', action='store_true', help='Fetch data from servers.')
        parser.add_argument('-c','--config', help='JSON config file', default="configs/newsletter_db.json")
        parser.add_argument('-d', '--debug', action='store_true', help='dump files')
        args = parser.parse_args()
        return args

    def main(self):
        self.registerPlugins()

        if self.args.refresh:
            self.flydivePluginManager.initAirports()
            self.flydivePluginManager.initConnections()

        # if self.args.fetchdetails:
        # newsletter_CfgList = self.newsletterMgr.get()
        newsletter_CfgList = self.newsletterMgr.unpack()
        self.flydiveScheduler.dumpToFile("Newsletter_CfgList.txt", newsletter_CfgList)

        flightTree, connectionList = self.flydiveScheduler.getConnectionsTree([ x for y in newsletter_CfgList for x in
                                                                               list(y.keys())], self.enabled_airlines)
        self.flydiveScheduler.dumpToFile("connectionsTree.txt", flightTree)

        # # Register all FlyDive plugins
        config = self.flydiveScheduler.getScheduleConfiguration(newsletter_CfgList)

        if self.args.refresh:
            self.flydivePluginManager.start(flightTree, connectionList, config)

        scheduledFlights = self.flydiveScheduler.collectFlighDetails(flightTree, config, newsletter_CfgList)
        
        self.flydiveScheduler.dumpToFile("collectFlighDetails.txt", scheduledFlights)

        filteredFlightPack = self.flydiveScheduler.filterFlightPack(scheduledFlights, newsletter_CfgList)
        self.flydiveScheduler.dumpToFile("filteredFlightPack.txt", filteredFlightPack)

        calculatedFlights = self.flydiveScheduler.calculateCosts(filteredFlightPack)
        self.flydiveScheduler.dumpToFile("calculateCosts.txt", calculatedFlights)

        self.newsletter.prepare_HTML(calculatedFlights)
        return
