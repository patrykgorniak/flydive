from wizzair.wizzairdl import WizzairDl
from wizzair.WizzairParser import WizzairParser
from wizzair import commonUrls as WizzData
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
from common import tools
from monthdelta import monthdelta
import datetime
import locale

class WizzairPlugin(object):

    """Docstring for WizzairPlugin. """

    def __init__(self):
        self.carrierCode = WizzData.carrierCode
        self.airline_name = WizzData.airline_name

        self._dlMgr = WizzairDl()
        self.parser = WizzairParser()
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

        self.__fetchAndAddAirports()
        self.__fetchAndAddConnections()

        con = Connections()
        connections = self.db.queryFilteredConnections(con)

        date_from = datetime.datetime.now()
        date_to = datetime.datetime.now()
        oneSideConnections = self.filterConnectionsOneDirection(connections);
        # for c in oneSideConnections:
        #     print(c)
        self.__fetchAndAddFlightDetails(connections, date_from, date_to)



    def __fetchAndAddFlightDetails(self, connections, datetime_from, datetime_to):
        """TODO: Docstring for __fetchAndAddFlightDetails.

        :connections: TODO
        :datetime_from: TODO
        :datetime_to: TODO
        :returns: TODO

        """
        if len(connections) == 0:
            raise ValueError('Connections are empty')



    def __fetchAndAddConnections(self):
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        self.log("Fetching and adding connections");
        testFilter = self.__generateConnections()

        for connectionsFromAirport in self._dlMgr.getConnections():
            self.__unpackAndAddToDb(connectionsFromAirport, testFilter)

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

    def __generateConnections(self):
        """TODO: Docstring for __generateConnections.
        :returns: TODO

        """
        con = {'WAW': 'LTN', 'LTN':'WAW'}
        return con

    def __initAirline(self):
        """TODO: Docstring for __addAirline.
        :returns: TODO

        """
        self.log("Add airline {0}".format(self.carrierCode))
        airline = Airline(carrierCode=self.carrierCode, airlineName=self.airline_name)
        self.db.addAirline(airline)

    def __unpackAndAddToDb(self, connection, filter_by = {}):
        """TODO: Docstring for __extractConnection.

        :connection: TODO
        :returns: TODO

        """
        connectionList = self.parser.extractJSONConnectionToList(connection)
        for c in connectionList:
            c.id = self.db.addConnection(c)
            #TODO: Added connections to DB, filter OneDirectionConnection

            # if filter_by:
            #     if ASL['SC'] in filter_by:
            #         if filter_by[ASL['SC']] == connection['DS']:
            #             self.__fetchFlightTimeTable(self.month_delta, connections)
            # else:
            #     self.__fetchFlightTimeTable(self.month_delta, connections)


    def __fetchAndAddAirports(self):
        """TODO: Docstring for getAirports.

        :returns: TODO

        """
        self.log("Fetching and adding airports");
        for row in self._dlMgr.getAirports():
            if row is not None:
                airport = Airport(iata=row['IATA'], 
                                  name=row['ShortName'],
                                  latitude=row['Latitude'], 
                                  longitude=row['Longitude'], 
                                  country='N/A')
                self.db.addAirport(airport)

    def filterConnectionsOneDirection(self, connections):
        """TODO: Docstring for filterConnectionsOneDirection.

        :connections: TODO
        :returns: TODO

        """
        oneDirectionConnection = []
        for c in connections:
            c_return = Connections(src_iata=c.dst_iata, dst_iata=c.src_iata)
            if not c or not c_return in oneDirectionConnection:
                oneDirectionConnection.append(c)

        return oneDirectionConnection


    def __fetchFlightTimeTable(self, monthDelta, connection):
        """TODO: Docstring for __fetchTimeTable.

        :monthDelta: TODO
        :returns: TODO

        """
        flightsTimeTableDetails = []

        if connection is not None:
            connections = [connection.__dict__]
            self.log(connections)
        else:
            connections = self.db.queryConnections()

        for c in connections:
            self.log('Connection: {0}'.format(c))
            for delta in range(monthDelta):
                date = self.currentDate + monthdelta(delta)
                details = {'src_iata': c['src_iata'], 
                           'dst_iata': c['dst_iata'], 
                           'month': date.month,
                           'year': date.year 
                           }
                flightDetails = self._dlMgr.fetchFlightDetails(details)
                flightsTimeTableDetails.append(flightDetails)

        for flightsInMonth in flightsTimeTableDetails:
            for flight in flightsInMonth:
                if flight['Flights']: # check if there are flights that day
                    self.__addFlightDetails(flight, connection.id)

    def __addFlightDetails(self, flight, connection_ID):
        """TODO: Docstring for __addFlightDetails.

        :flight: TODO
        :returns: TODO

        """
        if len(flight['Flights']) == 0:
            flightObj = self.__convertToFlightDetailsObject(flight, connection_ID)
            self.db.addFlightDetails(flightObj)
        else:
            pass
            # Search for updated prices for flights from-to
            # self.__addFlightDetails(flight

    def __convertToFlightDetailsObject(self, flight, connection_ID):
        """TODO: Docstring for __convertToFlightDetailsObject.

        :flight: TODO
        :returns: TODO

        """
        STA = flight['Flights'][0]['STA']
        STD = flight['Flights'][0]['STD']
        departureDate = flight['CurrentDate'] + " " + STD
        arrivalDate = flight['CurrentDate'] + " " + STA
        departure = datetime.datetime.strptime(departureDate, "%Y-%m-%d %H:%M")
        arrival = datetime.datetime.strptime(arrivalDate, "%Y-%m-%d %H:%M")

        flightObj = FlightDetails(id_connections = connection_ID,
                                  departure_DateTime = departure,
                                  arrival_DateTime = arrival,
                                  price = str(flight['MinimumPrice']).replace(',','.').split(' ')[0],
                                  currency = str(flight['MinimumPrice']).split(' ')[1],
                                  flightNumber = flight['Flights'][0]['FlightNumber'],
                                  isMacStation = tools.str2Boolean(flight['Flights'][0]['IsMACStation']),
                                  isAirportChanged = tools.str2Boolean(flight['Flights'][0]['IsAirportChange'])
                                  )

        return flightObj


    def __fetchFlightDetails(self, flight):

        """TODO: Docstring for downloadData.
        :returns: TODO

        """
        return self._dlMgr.searchFlightDetails(flight)
        # for connection in self.db.queryConnections():
        #     print(connection.id);
            # print("{0} 1}".format(src, dst))
