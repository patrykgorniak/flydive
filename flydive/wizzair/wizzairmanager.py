from wizzair.wizzairdl import WizzairDl
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm

class WizzairPlugin(object):

    """Docstring for WizzairPlugin. """

    def __init__(self):
        self._dlMgr = WizzairDl()
        cfg = CfgMgr().getConfig()
        self.db = DatabaseManager(cfg['DATABASE']['name'], cfg['DATABASE']['type'])
        self.carrierCode = 'W6'
        self.airline_name = 'Wizz Air'
        self.__initAirline()

    def log(self, message):
        lm.debug("WizzairPlugin: {0}".format(message))


    def run(self):
        """TODO: Docstring for run.
        :returns: TODO

        """
        self.__fetchAirports()
        self.__fetchConnections()
        self.__fetchFlightDetails()

    def __fetchConnections(self):
        self.log("Fetch connections");
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        for connection in self._dlMgr.getConnections():
            self.__extractConnection(connection)

    def __initAirline(self):
        """TODO: Docstring for __addAirline.
        :returns: TODO

        """
        self.log("Add airline {0}".format(self.carrierCode))
        airline = Airline(carrierCode=self.carrierCode, airlineName=self.airline_name)
        self.db.addAirline(airline)

    def __extractConnection(self, connection):
        """TODO: Docstring for __extractConnection.

        :connection: TODO
        :returns: TODO

        """
        for ASL in connection['ASL']:
            self.log("From: {0} to {1}".format(ASL['SC'], connection['DS']))
            connections = Connections(src_iata=ASL['SC'], dst_iata=connection['DS'], carrierCode=self.carrierCode)
            self.db.addConnection(connections)

    def __fetchAirports(self):
        """TODO: Docstring for getAirports.

        :returns: TODO

        """
        self.log("fetchAirports");
        for row in self._dlMgr.getAirports():
            if row is not None:
                airport = Airport(iata=row['IATA'], name=row['ShortName'],
                                  latitude=row['Latitude'], longitude=row['Longitude'], country='N/A')
                self.db.addAirport(airport)

    def __fetchFlightDetails(self):

        """TODO: Docstring for downloadData.
        :returns: TODO

        """
        for src, dst in self.db.queryConnections({dst_iata:"WAW"}):
            print("{0} {1}".format(src, dst))
