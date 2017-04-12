import json
import datetime
from common import tools
from monthdelta import monthdelta
from common.ConfigurationManager import CfgMgr
from common.DatabaseManager import DatabaseManager
from common.AlgorithmsSupport import BFS
from common.DatabaseModel import *
from common import LogManager as lm
from flight_scheduler.SearchEngine import FLSearchEngine

class FlightScheduler():

    """Docstring for FlightScheduler. """

    def __init__(self):
        self.cfg = CfgMgr().getConfig()
        self.flse = FLSearchEngine()
        self.departure_cities = json.loads(self.cfg['FLIGHT_SEARCH']['departure_cities'])
        self.arrival_cities = json.loads(self.cfg['FLIGHT_SEARCH']['arrival_cities'])
        self.search_depth = int(self.cfg['FLIGHT_SEARCH']['search_depth'])
        self.excluded_cities = json.loads(self.cfg['FLIGHT_SEARCH']['excluded_cities'])

        # READ CONFIG DATA
        self.db = DatabaseManager(self.cfg['DATABASE']['name'],
                                  self.cfg['DATABASE']['type'],
                                  self.cfg['DATABASE']['server'],
                                  self.cfg['DATABASE']['pass'],
                                  self.cfg['DATABASE']['user'] )

    def log(self, message):
        lm.debug("FlightScheduler: {0}".format(message))

    def collectFlighDetails(self, directionList, config = {'date_from' : -1, 'date_to': -1 }):
        date_from = config['date_from'] #datetime.datetime.now() + monthdelta(config['deltaTimeMonths_from'])
        date_to = config['date_to'] #date_from + monthdelta(config['deltaTimeMonths_to'])

        connections = {}
        flightDetails = {}
        scheduledFlights = {}
        for direction in directionList:
            airports = []
            back_airports = []
            main_key = "-".join(direction)
            back_main_key = "-".join(direction[::-1])
            self.log(main_key)
            for i in range(len(direction) - 1):
                from_iata = direction[i]
                to_iata = direction[i+1]
                key = "{}-{}".format(from_iata, to_iata)
                back_key = "{}-{}".format(to_iata, from_iata)
                airports.append(key)
                back_airports.append(back_key)
                if key not in connections:
                    value = Connections(src_iata = from_iata, dst_iata = to_iata)
                    back_value = Connections(src_iata = to_iata, dst_iata = from_iata)
                    connections[key] = value
                    connections[back_key] = back_value
                    flightDetails[key] = self.db.queryFlightDetails(value, True, date_from, date_to)
                    flightDetails[back_key] = self.db.queryFlightDetails(back_value, True, date_from, date_to)

            scheduledFlights[main_key] = self.flse.schedulePath(airports, flightDetails)
            scheduledFlights[back_main_key] = self.flse.schedulePath(back_airports, flightDetails)

            # for directionName, directionList in scheduledFlights.items():
            #     for direction in directionList:
            #         self.log(direction)
            #         for changeName, flightsList in direction.items():
            #             self.log(changeName)
            #             if type(flightsList) is list:
            #                 for flight in flightsList:
            #                     self.log(flight)

        with open("flights.txt",'w') as f:
            json.dump(scheduledFlights, f, cls=tools.FLJsonEncoder, indent=4)
        f.close()

        return scheduledFlights

    def getConnectionsTree(self):
        paths = []
        connectionList = self.db.getConnections()
        graph = tools.dumpConnectionsToGraph(connectionList, self.excluded_cities)

        for src_iata in self.departure_cities:
            for dst_iata in self.arrival_cities:
                paths.extend(BFS(graph, self.search_depth, src_iata, dst_iata))
        
        with open("connectionsTree.txt",'w') as f:
            json.dump(paths, f, cls=tools.FLJsonEncoder, indent=4)
        f.close()
        
        with open("graph.txt",'w') as f:
            json.dump(graph, f, cls=tools.FLJsonEncoder, indent=4)
        f.close()
        
        return paths, connectionList

    def getScheduleConfiguration(self):
        """TODO: Docstring for getScheduleConfiguration.
        :returns: TODO

        """
        config = {  }
        month_delta = int(self.cfg['FLIGHT_SEARCH']['month_delta'])
        delay_data = datetime.timedelta(days=7)
        date_from = datetime.datetime.now() + delay_data;
        date_to = date_from + monthdelta(month_delta)

        config['date_from'] = date_from
        config['date_to'] = date_to

        return config
