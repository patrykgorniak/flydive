import collections
from wizzair.wizzairdl import WizzairDl
from wizzair.WizzairParser import WizzairParser
from wizzair import commonUrls as WizzData
from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from common.ConfigurationManager import CfgMgr
from common.GeoNameProvider import GeoNameProvider
from common import LogManager as lm
from common import tools
from monthdelta import monthdelta
from common.SessionManager import SessionManager
from common.AlgorithmsSupport import BFS
from common.FLPlugin import FLPlugin
import datetime
from time import sleep
import locale
import queue
import json
import threading

class WizzairPlugin(FLPlugin):
    def __init__(self, asyncDlMgr = None):
        FLPlugin.__init__(self)
        self.carrierCode = WizzData.carrierCode
        self.airline_name = WizzData.airline_name
        self.return_q = queue.Queue()
        self._asyncDlMgr = asyncDlMgr
        self._dlMgr = WizzairDl()
        self.parser = WizzairParser()
        self.geo_name = GeoNameProvider()
        self.cfg = CfgMgr().getConfig()

        # READ CONFIG DATA
        self.db = DatabaseManager(self.cfg['DATABASE']['name'],
                                  self.cfg['DATABASE']['type'],
                                  self.cfg['DATABASE']['server'],
                                  self.cfg['DATABASE']['pass'],
                                  self.cfg['DATABASE']['user'] )

        self.month_delta =int(self.cfg['FLIGHT_SEARCH']['month_delta'])
        self.flight_detail_bypass = str(self.cfg['DEBUGGING']['flight_detail_bypass'])=='on'
        self.asyncMode = str(self.cfg['DOWNLOAD_MANAGER']['async_mode'])=='on'
        self.dump_restore_session = str(self.cfg['GENERAL']['dump_restore_session'])=='on'
        self.departure_cities = json.loads(self.cfg['FLIGHT_SEARCH']['departure_cities'])
        self.arrival_cities = json.loads(self.cfg['FLIGHT_SEARCH']['arrival_cities'])
        self.search_depth = int(self.cfg['FLIGHT_SEARCH']['search_depth'])
        self.excluded_cities = json.loads(self.cfg['FLIGHT_SEARCH']['excluded_cities'])

        self.currentDate = datetime.datetime.now()
        self.session = SessionManager(self.airline_name)

        if not self.flight_detail_bypass and self.asyncMode and self._asyncDlMgr is not None:
            self.receiver = threading.Thread(target=self.asyncReceiver)
            self.receiver.start()

    def log(self, message):
        lm.debug("WizzairPlugin: {0}".format(message))

    def build_tree(self, scheduledFlights, previousFlight, flightList, lastFlight, flightDetailList, criteria):
        """TODO: Docstring for build_tree.

        :current_flight: list of possible previous flight change in format FlighDetails
        :flightList: list of flights in format FROM-TO
        :last_flight: last flight on the list in format FROM-TO
        :flightDetailList: list of all flight details 
        :criteria: criteria for searching such as time_change_{min, max}
        :returns: TODO

        """
        # self.log("scheduled flight: {}".format(scheduledFlights))
        # self.log("Previous flight: {}".format(previousFlight))
        # self.log("Flight list: {}".format(flightList))
        # self.log("Last flight: {}".format(lastFlight))

        if flightList[0] == lastFlight:
            scheduledFlights[flightList[0]] = self.findFlight(previousFlight, flightDetailList[flightList[0]], criteria)
            return scheduledFlights
        else:
            scheduledFlights[flightList[0]] = self.findFlight(previousFlight, flightDetailList, criteria)
            return self.build_tree(scheduledFlights, flightList[0], flightList[1:], flightList[-1], flightDetailList, criteria)

    def findFlight(self, previousFlight, flightDetails, criteria):
        """TODO: Docstring for findFlight.

        :flightFrom: TODO
        :next_airport_key: TODO
        :flightDetails: TODO
        :criteria: TODO
        :returns: TODO

        """
        timedelta_min = datetime.timedelta(hours=criteria['time_change_min'])
        timedelta_max = datetime.timedelta(hours=criteria['time_change_max'])
        found_flights = [x for x in flightDetails if x.departure_DateTime >= previousFlight.arrival_DateTime + timedelta_min and
         x.departure_DateTime <= previousFlight.arrival_DateTime + timedelta_max]

        return found_flights

    def schedulePath(self,  airportList, flightDetails, criteria = { 'time_change_min': 2, 'time_change_max': 12 }):
        """TODO: Docstring for schedulePath.

        :path: TODO
        :returns: TODO

        """
        self.log(airportList)
        scheduledFlights = []

        for start_flight in flightDetails[airportList[0]]:
            scheduled = {}
            scheduled[airportList[0]] = [start_flight]
            scheduledFlights.append(self.build_tree(scheduled, start_flight, airportList[1:], airportList[-1], flightDetails,
                    criteria ))
        return scheduledFlights

    def runAlgorithm(self, paths):
        """TODO: Docstring for runAlgorithm.

        :paths: TODO
        :returns: TODO

        """
        max_time_change = 4

        connections = {}
        flightDetails = {}
        scheduledFlights = {}
        for path in paths[1:-1]:
            airports = []
            main_key = "{}-{}".format(path[0], path[-1])
            for i in range(len(path) - 1):
                from_iata = path[i]
                to_iata = path[i+1]
                key = "{}-{}".format(from_iata, to_iata)
                airports.append(key)
                if key not in connections:
                    value = Connections(src_iata = from_iata, dst_iata = to_iata)
                    connections[key] = value
                    flightDetails[key] = self.db.queryFlightDetails(value, datetime.datetime.now(),
                                                                    datetime.datetime.now() + monthdelta(1))
            scheduledFlights[main_key] = self.schedulePath(airports, flightDetails)
            self.log(scheduledFlights[main_key][0])
            for key in scheduledFlights[main_key][0]:
                self.log(key)
                for value in scheduledFlights[main_key][0][key]:
                    self.log(value)
            return


        # for elem in db:
        #     self.log("My data: {}".format(elem))
        #     self.log("My data: {}".format(elem.connection))

    def run(self):
        self.__initAirline()
        self.connections = []
        self.proceedList = []
        paths = []
        # date_from = datetime.datetime(2016,12,10) # this is only for test
        delay_data = datetime.timedelta(days=7)
        date_from = self.currentDate + delay_data;
        date_to = date_from + monthdelta(self.month_delta)
        self.log("Flights update between: {} - {}".format(date_from, date_to))

        self.__fetchAndAddAirports()
        self.__fetchAndAddConnections()
        graph = tools.dumpConnectionsToGraph(self._dlMgr.getConnections(), self.excluded_cities)

        for src_iata in self.departure_cities:
            for dst_iata in self.arrival_cities:
                paths.extend(BFS(graph, self.search_depth, src_iata, dst_iata))

        file = open("paths.txt", "w")
        for path in paths:
            file.write("{}\n".format(path))
        file.close()

        self.runAlgorithm(paths)
        return 

        connectionQueryList = self.prepareConnectionsQuery(paths)
        self.connections.extend(self.db.getConnectionList(connectionQueryList))


        if self.dump_restore_session and self.session.isSaved():
            self.connections.extend(self.session.restoreSession())
            self.session.close()
        # else:
        #     self.connections.extend(self.db.getOrderedConnections())

        oneWayIdxList = self.getOneWayConnectionIndexList(self.connections);
        # self.log("Dupplicates: {}".format([item for item, count in collections.Counter(oneWayIdxList).items() if count>1]))
        # for i in self.connections:
        #     self.log(i)
        # self.log("Oneway connection IDXs:\n{}".format(oneWayIdxList))

        # self.log("OneWayIdxList: {} \nConnections: {}".format(len(oneWayIdxList),len(self.connections)))
        assert (len(oneWayIdxList)*2) == len(self.connections)

        if not self.flight_detail_bypass:
            try:
                self.getFlightDetails(date_from, date_to, oneWayIdxList)
            except:
                if self.dump_restore_session:
                    lm.debug("Session dumped!")
                    connectionsLeftList = []
                    if len(self.proceedList) % 2 != 0:
                        self.proceedList.pop()
                    connectionsLeftList.extend([x for x in connections if x not in self.proceedList])
                    if(len(connectionsLeftList)):
                        self.session.save(connectionsLeftList)
                    raise

        if not self.flight_detail_bypass and self.asyncMode:
            self.receiver.join()
        self.log("Total time: {}".format(datetime.datetime.now() - self.currentDate))

    def prepareConnectionsQuery(self, paths):
        queryList = []
        for path in paths:
            for i in range(len(path) - 1):
                queryList.append(Connections(src_iata=path[i], dst_iata=path[i+1], carrierCode = self.carrierCode))
                queryList.append(Connections(src_iata=path[i+1], dst_iata=path[i], carrierCode = self.carrierCode))
        return queryList

    def __asyncGetFlightDetails(self, flight):
        flightDetailsJSON = self._dlMgr.getFlightDetails(flight)
        return self.parser.extractJSONFlightDetails(flightDetailsJSON)


    def __scheduleFlightDetails(self, flight):
        params = self._dlMgr.packParamsToJSON(flight)
        self._asyncDlMgr.schedulePostMethod(WizzData.CommonData.Search, params, self.return_q)

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
        self.log("Fetch and add connections")
        addedToDb = False
        # testFilter = self.__generateConnections()

        for connectionsFromAirport in self._dlMgr.getConnections():
            if self.__unpackAndAddToDb(connectionsFromAirport):
                addedToDb = True
        return addedToDb

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
        self.log("Add airline {0}".format(self.carrierCode))
        airline = Airline(carrierCode=self.carrierCode, airlineName=self.airline_name)
        self.db.addAirline(airline)

    def __unpackAndAddToDb(self, connection, filter_by = {}):

        addedToDb = False
        connectionList = self.parser.extractJSONConnectionToList(connection)

        for c in connectionList:
            if self.db.addConnection(c):
                addedToDb = True
        return addedToDb

    def __fetchAndAddAirports(self):
        """
        """
        self.log("Fetch and add airports")
        airports = self.parser.extractJSONAirportsToList(self._dlMgr.getAirports())
        for airport in airports:
            if not self.db.exists(airport):
                airport = self.geo_name.getGeoData(airport)
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

    def asyncReceiver(self):
        print("Receiver started!")
        while True:
            flightDetailsJSON = self.return_q.get()
            list = self.parser.extractJSONFlightDetails(flightDetailsJSON)
            self.handleFlightDetails(list)
            self.return_q.task_done()

            if self.return_q.empty():
                sleep(15)
            if self.return_q.empty():
                return None


    def handleFlightDetails(self, flightDetalsList):
        for item in flightDetalsList:
            # self.log(item)
            connection = [x for x in self.connections if x==item][0]  #TODO: should be changed, maybe to HASH MAP
            item.id_connections = connection.id
            self.db.addFlightDetails(item)

        connection.updated =  datetime.datetime.now().date()
        self.db.updateConnection(connection)


    def getFlightDetails(self, date_from, date_to, oneWayIdxList):
        for i, idx in enumerate(oneWayIdxList):
            for delta in range(self.month_delta):
                time = date_from + monthdelta(delta)

                timeTableList = self.__getTimeTable(time, self.connections[idx]) #get timetable for given year-month
                for flight in timeTableList:
                    if flight.date > date_from and flight.date <= date_to: #datetime.datetime(2017,2,18):
                        if self.asyncMode:
                            self.__scheduleFlightDetails(flight)
                        else:
                            list = self.__getFlightDetails(flight)
                            self.handleFlightDetails(list)
            self.proceedList.append(self.connections[idx])
            lm.debug("Status: {} of {} - ({}%)".format(i + 1, len(oneWayIdxList), (i+1)/len(oneWayIdxList)*100))
