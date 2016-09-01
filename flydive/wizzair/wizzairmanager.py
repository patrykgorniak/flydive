from wizzair.wizzairdl import WizzairDl
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm

class WizzairPlugin(object):

    """Docstring for WizzairPlugin. """

    def __init__(self):
        self._dlMgr = WizzairDl()
        cfg = CfgMgr().getConfig()
        self.db = DatabaseManager(cfg['DATABASE']['name'], cfg['DATABASE']['type'])

    def log(self, message):
        lm.debug("WizzairPlugin: {0}".format(message))

    def fetchConnections(self):
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        self.log("fetchConnections");
        return self._dlMgr.getConnections()

    def fetchAirports(self):
        """TODO: Docstring for getAirports.

        :returns: TODO

        """
        self.log("fetchAirports");
        for row in self._dlMgr.getAirports():
            if row is not None:
                airport = Airport(iata=row['IATA'], name=row['ShortName'],
                                  latitude=row['Latitude'], longitude=row['Longitude'], country='N/A')
                self.db.addAirport(airport)

    def downloadData(self):

        """TODO: Docstring for downloadData.
        :returns: TODO

        """
        pass
