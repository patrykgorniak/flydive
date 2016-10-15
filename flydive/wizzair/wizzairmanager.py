from wizzair.wizzairdl import WizzairDl
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
from monthdelta import monthdelta
import datetime

class WizzairPlugin(object):

    """Docstring for WizzairPlugin. """

    def __init__(self):
        self.carrierCode = 'W6'
        self.airline_name = 'Wizz Air'

        self._dlMgr = WizzairDl()
        self.cfg = CfgMgr().getConfig()
        self.db = DatabaseManager(self.cfg['DATABASE']['name'], self.cfg['DATABASE']['type'])
        self.month_delta =int(self.cfg['FLIGHTS']['month_delta'])
        self.currentDate = datetime.datetime.now()

        self.__initAirline()

    def log(self, message):
        lm.debug("WizzairPlugin: {0}".format(message))


    def run(self):
        """TODO: Docstring for run.
        :returns: TODO

        """
        testFilter = self.__getTestConnections()

        self.__fetchAirports()
        self.__fetchConnections()
        self.__fetchFlightTimeTable(self.month_delta, testFilter)

    def __fetchConnections(self):
        self.log("Fetch connections");
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        for connection in self._dlMgr.getConnections():
            self.__extractConnection(connection)

    def __getTestConnections(self):
        """TODO: Docstring for __getTestConnections.
        :returns: TODO

        """
        testDate = [
            { 'src_iata': 'WAW', 'dst_iata': 'LTN' },
            { 'src_iata': 'LTN', 'dst_iata': 'WAW' },
            { 'src_iata': 'ABZ', 'dst_iata': 'GDN' },
            { 'src_iata': 'GDN', 'dst_iata': 'ABZ' },
            { 'src_iata': 'WRO', 'dst_iata': 'EIN' }
        ]
        return testDate

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

    def __fetchFlightTimeTable(self, monthDelta, testFilter = None):
        """TODO: Docstring for __fetchTimeTable.

        :monthDelta: TODO
        :returns: TODO

        """
        flightsTimeTableDetails = []

        if testFilter is not None:
            if self.cfg['DEBUGGING']['state'] == 'online':
                raise Exception('Used filter for test with online testing!')
            connections = testFilter
            self.log(connections)
        else:
            connections = self.db.queryConnections()

        for c in connections:
            self.log(c)
            for delta in range(monthDelta):
                date = self.currentDate + monthdelta(delta)
                details = {'src_iata': c['src_iata'], 'dst_iata': c['dst_iata'], 'month': date.month,
                           'year': date.year }
                # self.log(details)
                flightsTimeTableDetails.append(self._dlMgr.fetchFlightDetails(details))

        for flights in flightsTimeTableDetails:
            for flight in flights:
                if flight['Flights']:
                    self.__addFlightDetails(flight)

    def __addFlightDetails(self, flight):
        """TODO: Docstring for __addFlightDetails.

        :flight: TODO
        :returns: TODO

        """
        pass
        # print(flight)
        # print()

    def __fetchFlightDetails(self, ):

        """TODO: Docstring for downloadData.
        :returns: TODO

        """
        for connection in self.db.queryConnections():
            print(connection.id);
            # print("{0} {1}".format(src, dst))
