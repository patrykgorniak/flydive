import datetime
import locale
import queue
import json
import threading
import collections
import sys

from common.DatabaseManager import DatabaseManager
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails, Statistics
from common.ConfigurationManager import CfgMgr
from common.GeoNameProvider import GeoNameProvider
from common import LogManager as lm
from common import tools
from common.SessionManager import SessionManager
from common.AlgorithmsSupport import BFS
from common.FLPlugin import FLPlugin

from time import sleep
from monthdelta import monthdelta

class FLEngineCreator(FLPlugin):

    """Docstring for FLEngineCreator. """

    def __init__(self, cfg, parser, downloader, common, dbManager, sessionManager, use_post_for_async, asyncDlMgr = None):
        FLPlugin.__init__(self)
        self.carrierCode = common.carrierCode
        self.airline_name = common.airline_name
        self.common = common
        self.return_q = queue.Queue()
        self.geo_name = GeoNameProvider()
        self.parser = parser
        self.dlMgr = downloader
        self.db = dbManager
        self.cfg = cfg
        self.asyncDlMgr = asyncDlMgr
        self.use_post = use_post_for_async

        self.__readConfigData()
        self.currentDate = datetime.datetime.now()

        self.statistics = Statistics()
        self.__initAirline()


    def initAirports(self):
        self.__fetchAndAddAirports()
        self.airportsReady = True

    def initConnections(self):
        assert self.airportsReady == True, "Airports were not initialized!"
        self.__fetchAndAddConnections()
        self.connectionsReady = True

    def run(self, paths, connectionList, config):
        # assert self.airportsReady == True, "Airports were not initialized!"
        # assert self.connectionsReady == True, "Connections were not initialized!"
        assert config['date_from'] != -1 and config['date_to'] != -1, "Wrong config!"

        if not self.flight_detail_bypass and self.asyncMode and self.asyncDlMgr is not None:
            self.log("Starting thread")
            self.receiver = threading.Thread(target=self.__asyncReceiver)
            self.receiver.start()

        self.connections = []
        self.proceedList = []

        date_from = config['date_from'] #self.currentDate + delay_data;
        date_to = config['date_to'] #date_from + monthdelta(self.month_delta)
        self.log("Flights update between: {} - {}".format(date_from, date_to))

        self.connections.extend(self.__prepareConnectionsQuery(paths, connectionList))

        if self.dump_restore_session and self.session.isSaved():
            self.connections.extend(self.session.restoreSession())
            self.session.close()

        oneWayIdxList = self.__getOneWayConnectionIndexList(self.connections);
        self.log("Connections: {}".format(len(self.connections)))
        self.log("OneWayIdx: {}".format(len(oneWayIdxList)))

        assert (len(oneWayIdxList)*2) == len(self.connections)

        if not self.flight_detail_bypass:
            try:
                self.__getFlightDetails(date_from, date_to, oneWayIdxList)
            except:
                if self.dump_restore_session:
                    lm.debug("Session dumped!")
                    connectionsLeftList = []
                    if len(self.proceedList) % 2 != 0:
                        self.proceedList.pop()
                    connectionsLeftList.extend([x for x in connections if x not in self.proceedList])
                    if(len(connectionsLeftList)):
                        self.session.save(connectionsLeftList)

                print("Unexpected error:", sys.exc_info()[0])
                lm.exception()
                raise

        self.return_q.join()
        self.asyncDlMgr.finished(self.return_q)

        if not self.flight_detail_bypass and self.asyncMode:
            self.receiver.join()

        self.log("Total time: {}".format(datetime.datetime.now() - self.currentDate))

    def __getFlightDetails(self, date_from, date_to, oneWayIdxList):
        
        for i, idx in enumerate(oneWayIdxList):
            for delta in range(date_to.month - date_from.month + 1):
                time = date_from + monthdelta(delta)

                timeTableList = self.__getTimeTable(time, self.connections[idx]) #get timetable for given year-month
                for flight in timeTableList:
                    if flight.date >= date_from and flight.date <= date_to: #datetime.datetime(2017,2,18):
                        if self.asyncMode:
                            self.__scheduleFlightDetails(flight)
                        else:
                            list = self.__fetchFlightDetails(flight)
                            self.__handleFlightDetails(list)

            self.proceedList.append(self.connections[idx])
            lm.debug("Status: {} of {} - ({}%)".format(i + 1, len(oneWayIdxList), (i+1)/len(oneWayIdxList)*100))

    def __fetchFlightDetails(self, flight):
        """ Gets details of flight

        :flight: TODO
        :returns: TODO

        """
        flightDetailsJSON = self.dlMgr.getFlightDetails(flight)
        return self.parser.extractJSONFlightDetails(flightDetailsJSON)

    def __scheduleFlightDetails(self, flight):
        if self.use_post:
            params = self.dlMgr.packParamsToJSON(flight)
            self.asyncDlMgr.schedulePostMethod(self.common.CommonData.Search, params, self.return_q)
        else:
            url = self.dlMgr.prepareUrl(flight)
            self.asyncDlMgr.scheduleGetMethod(url, self.return_q)

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

        timeTableJSON = self.dlMgr.getTimeTable(details)
        return self.parser.extractJSONTimeTable(timeTableJSON, details)

    def __getOneWayConnectionIndexList(self, connectionList):
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
            if not c_return in connectionList:
                continue
            if not c or not c_return in tmplist:
                oneWayIndexes.add(idx)
                tmplist.append(c)

        return list(oneWayIndexes)

    def __prepareConnectionsQuery(self, paths, connectionList):
        queryList = []
        for destName, flightDetails in paths.items():
            for path in flightDetails:
                for i in range(len(path) - 1):
                    queryList.extend([x for x in connectionList if (x.src_iata==path[i] and x.dst_iata==path[i+1] and
                                       x.carrierCode==self.carrierCode) or (x.src_iata==path[i+1] and x.dst_iata==path[i] and
                                       x.carrierCode==self.carrierCode) ])
                # connection = Connections(src_iata=path[i], dst_iata=path[i+1], carrierCode = self.carrierCode)
                # queryList.append(connection)
                # queryList.append(Connections(src_iata=path[i+1], dst_iata=path[i], carrierCode = self.carrierCode))
        return queryList

    def __asyncReceiver(self):
        while True:
            ret = self.return_q.get()
            flightDetailsJSON = ret['data']
            if flightDetailsJSON is None:
                self.log("End of async receiver")
                self.return_q.task_done()
                break

            url = ret['url']
            # self.log(url)
            list = self.parser.extractJSONFlightDetails(flightDetailsJSON)
            self.__handleFlightDetails(list)
            self.return_q.task_done()

#             if self.return_q.empty():
#                 sleep(30)
#             if self.return_q.empty():
#                 return None

    def __handleFlightDetails(self, flightDetalsList):
        connection = None

        for item in flightDetalsList:
            connection = [x for x in self.connections if x==item][0]  #TODO: should be changed, maybe to HASH MAP
            item.id_connections = connection.id
            self.db.addFlightDetails(item)
            connection.updated =  datetime.datetime.now().date()

        if isinstance(connection, Connections):
            self.db.updateConnection(connection)

    def __readConfigData(self):
        self.month_delta = int(self.cfg['FLIGHT_SEARCH']['month_delta'])
        self.flight_detail_bypass = str(self.cfg['DEBUGGING']['flight_detail_bypass'])=='on'
        self.asyncMode = str(self.cfg['DOWNLOAD_MANAGER']['async_mode'])=='on'
        self.dump_restore_session = str(self.cfg['GENERAL']['dump_restore_session'])=='on'
        self.departure_cities = json.loads(self.cfg['FLIGHT_SEARCH']['departure_cities'])
        self.arrival_cities = json.loads(self.cfg['FLIGHT_SEARCH']['arrival_cities'])
        self.search_depth = int(self.cfg['FLIGHT_SEARCH']['search_depth'])
        self.excluded_cities = json.loads(self.cfg['FLIGHT_SEARCH']['excluded_cities'])

    def log(self, message):
        lm.debug("{}Plugin: {}".format(self.airline_name, message))

    def __initAirline(self):
        self.log("Add airline {0}".format(self.carrierCode))
        airline = Airline(carrierCode=self.carrierCode, airlineName=self.airline_name)
        self.db.addAirline(airline)
        self.statistics.airline_code = self.carrierCode

    def __fetchAndAddAirports(self):
        self.log("Fetch and add airports")
        airports = self.parser.extractJSONAirportsToList(self.dlMgr.getAirports())
        statistics = self.db.getStatistics(self.carrierCode)
        
        if statistics:
            statistics.airportCount == len(airports)
            self.log("Statistics: skip adding airports.")
            return

        for airport in airports:
            # if not self.db.exists(airport):
            airport = self.geo_name.getGeoData(airport)
            self.db.addAirport(airport)

        self.statistics.airportCount = len(airports)

    def __fetchAndAddConnections(self):
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        self.log("Fetch and add connections")
        addedToDb = False
        # testFilter = self.__generateConnections()

        connectionList = []
        for connectionsFromAirport in self.dlMgr.getConnections():
            connectionList.extend(self.parser.extractJSONConnectionToList(connectionsFromAirport))

        statistics = self.db.getStatistics(self.carrierCode)
        if statistics:
            statistics.connectionCount == len(connectionList)
            self.log("Statistics: skip adding connections.")
            return False

        self.__addConnections(connectionList)
        self.statistics.connectionCount = len(connectionList)
        self.db.addStatistics(self.statistics)

    def __addConnections(self, connectionList, filter_by = {}):
        for c in connectionList:
            if self.db.addConnection(c):
                addedToDb = True
        return addedToDb
