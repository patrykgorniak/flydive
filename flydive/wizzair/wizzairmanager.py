from wizzair.wizzairdl import WizzairDl
from wizzair.WizzairParser import WizzairParser
from wizzair import commonUrls as WizzData
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from common.ConfigurationManager import CfgMgr
from common import LogManager as lm
from common import tools
from monthdelta import monthdelta
from common.SessionManager import SessionManager
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
        self.session = SessionManager(self.airline_name)

        self.__initAirline()

    def log(self, message):
        lm.debug("WizzairPlugin: {0}".format(message))


    def run(self):
        """TODO: Docstring for run.
        :returns: TODO

        """
        connections = []
        proceedList = []
        try:
            # date_from = datetime.datetime(2016,12,10) # this is only for test
            date_from = datetime.datetime.now()

            self.__fetchAndAddAirports()
            self.__fetchAndAddConnections()

            if self.session.isSaved():
                connections.extend(self.session.restoreSession())
                # self.session.close()
            else:
                connections.extend(self.db.getConnections())
                # con = Connections(src_iata='LTN', dst_iata='WAW')
                # connections.extend(self.db.getConnections(con))

            oneWayIdxList = self.getOneWayConnectionIndexList(connections);

            assert (len(oneWayIdxList)*2) == len(connections)

            for i, idx in enumerate(oneWayIdxList):
                for delta in range(self.month_delta):
                    time = date_from + monthdelta(delta)

                    timeTableList = self.__getTimeTable(time, connections[idx]) #get timetable for given year-month
                    for flight in timeTableList:
                        if flight.date > date_from and flight.date < datetime.datetime(2017,1,2):
                            list = self.__getFlightDetails(flight)
                            for item in list:
                                item.id_connections = [x for x in connections if x==item][0].id
                                lm.debug(item)
                                self.db.addFlightDetails(item)
                proceedList.append(connections[idx])
                lm.debug("Status: {} of {} - ({}%)".format(i, len(oneWayIdxList), i/len(oneWayIdxList)*100))

            self.log("Total time: {}".format(datetime.datetime.now() - date_from))
        except:

            lm.debug("Session dumped!")
            connectionsLeftList = []
            connectionsLeftList.append([x for x in connections if x not in proceedList])
            self.session.save(connectionsLeftList)
            raise

    def __fetchAndAddFlightDetails(self, connections, datetime_from, datetime_to):
        """TODO: Docstring for __fetchAndAddFlightDetails.

        :connections: TODO
        :datetime_from: TODO
        :datetime_to: TODO
        :returns: TODO

        """
        if len(connections) == 0:
            raise ValueError('Connections are empty')
        for delta in range(monthDelta):
            date = self.currentDate + monthdelta(delta)

    def __getFlightDetails(self, flight):
        """ Gets details of flight

        :flight: TODO
        :returns: TODO

        """
        flightDetailsJSON = self._dlMgr.getFlightDetails(flight)
        return self.parser.extractJSONFlightDetails(flightDetailsJSON)

    def __fetchAndAddConnections(self):
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        self.log("Fetching and adding connections");
        # testFilter = self.__generateConnections()

        for connectionsFromAirport in self._dlMgr.getConnections():
            self.__unpackAndAddToDb(connectionsFromAirport)

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
        """
        """
        self.log("Fetching and adding airports");

        airports = self.parser.extractJSONAirportsToList(self._dlMgr.getAirports())
        for airport in airports:
            self.db.addAirport(airport)

    def getOneWayConnectionIndexList(self, connectionList):
        """ Extracts one way connections from list of connections.

        :connectionList: list of Connections
        :returns: list of indexes of one way connections in connection list

        """
        if not isinstance(connectionList[0], Connections):
            raise TypeError

        oneWayIndexes = set()
        tmplist = []

        for idx, c in enumerate(connectionList):
            c_return = Connections(src_iata=c.dst_iata, dst_iata=c.src_iata)
            if not c or not c_return in tmplist:
                oneWayIndexes.add(idx)
                tmplist.append(c)

        return list(oneWayIndexes)

    def extractOneWayConnections(self, connections):
        """ Extracts one way connections from list of connections.

        :connections: list of connections
        :returns: list of indexes of one way connections in connection list

        """
        oneDirectionConnection = []
        for c in connections:
            c_return = Connections(src_iata=c.dst_iata, dst_iata=c.src_iata)
            if not c or not c_return in oneDirectionConnection:
                oneDirectionConnection.append(c)

        return oneDirectionConnectiony

    def __getTimeTable(self, date, connection):
        """ Gets monthly time table for connections and date

        :date: date (with year and month) for time table
        :connection: connection we need time table for
        :returns: list of TimeTables for month

        """
        self.log('Connection: {0}'.format(connection))
        details = {'src_iata': connection.src_iata,
                   'dst_iata': connection.dst_iata,
                   'month': date.month,
                   'year': date.year
                   }

        timeTableJSON = self._dlMgr.getTimeTable(details)
        return self.parser.extractJSONTimeTable(timeTableJSON)


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
