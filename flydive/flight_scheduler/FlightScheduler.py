import json
import datetime
import os
import copy
from common import tools
from monthdelta import monthdelta
from common.ConfigurationManager import CfgMgr
from common.DatabaseManager import DatabaseManager
from common.AlgorithmsSupport import BFS
from common.DatabaseModel import *
from common.CurrencyProvider import CurrencyProvider
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
        self.currencyProvider = CurrencyProvider()

        # READ CONFIG DATA
        self.db = DatabaseManager(self.cfg['DATABASE']['name'],
                                  self.cfg['DATABASE']['type'],
                                  self.cfg['DATABASE']['server'],
                                  self.cfg['DATABASE']['pass'],
                                  self.cfg['DATABASE']['user'] )
        self.log_dir = "logs"

    def log(self, message):
        lm.debug("FlightScheduler: {0}".format(message))

    def collectFlighDetails2(self, directionListSuite, config, newsletterSuite):

        tripList = []
        for trip in newsletterSuite:
            connections = {}
            flightDetails = {}
            scheduledFlightSuite = {}
            for dest, config in trip.items():
                scheduledFlights = {}
                toList = []
                returnList = []
                date_from = datetime.datetime.combine(config['start'], datetime.datetime.min.time())
                date_to = datetime.datetime.combine(config['end'], datetime.datetime.min.time())
                directionList = directionListSuite[dest]
                for direction in directionList:
                    airports = []
                    back_airports = []
                    # key = "{}-{}".format(direction[0], direction[-1])
                    main_key = "-".join(direction)
                    back_main_key = "-".join(direction[::-1])
                    self.log(main_key)
                    for i in range(len(direction) - 1):
                        from_iata = direction[i]
                        to_iata = direction[i+1]
                        key = "{}-{}".format(from_iata, to_iata)
                        back_key = "{}-{}".format(to_iata, from_iata)
                        airports.append(key)
                        back_airports.insert(0, back_key)
                        if key not in connections:
                            value = Connections(src_iata = from_iata, dst_iata = to_iata)
                            back_value = Connections(src_iata = to_iata, dst_iata = from_iata)
                            connections[key] = value
                            connections[back_key] = back_value
                            flightDetails[key] = self.db.queryFlightDetails(value, True, date_from, date_to)
                            flightDetails[back_key] = self.db.queryFlightDetails(back_value, True, date_from, date_to)

                    departTmp = self.flse.schedulePath(airports, flightDetails)
                    if len(departTmp) > 0:
                        scheduledFlights[main_key] = departTmp
                        toList.append({main_key: scheduledFlights[main_key]})

                    returnTmp = self.flse.schedulePath(back_airports, flightDetails)
                    if len(returnTmp) > 0:
                        scheduledFlights[back_main_key] = returnTmp
                        returnList.append({back_main_key: scheduledFlights[back_main_key]})

                scheduledFlightSuite[dest] = {"DEP": toList, "RET": returnList}
            tripList.append(scheduledFlightSuite)
        return tripList

    def collectFlighDetails(self, directionListSuite, config):
        date_from = config['date_from'] #datetime.datetime.now() + monthdelta(config['deltaTimeMonths_from'])
        date_to = config['date_to'] #date_from + monthdelta(config['deltaTimeMonths_to'])

        connections = {}
        flightDetails = {}
        scheduledFlightSuite = {}
        for dest, directionList in directionListSuite.items():
            scheduledFlights = {}
            for direction in directionList:
                airports = []
                back_airports = []
                # key = "{}-{}".format(direction[0], direction[-1])
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

                departList = self.flse.schedulePath(airports, flightDetails)
                if len(departList) > 0:
                    scheduledFlights[main_key] = departList

                returnList = self.flse.schedulePath(back_airports, flightDetails)
                if len(returnList) > 0:
                    scheduledFlights[back_main_key] = returnList

            scheduledFlightSuite[dest] = scheduledFlights

        return scheduledFlightSuite

    def getConnectionsTree(self, directionList):
        assert isinstance(directionList, list), "DirectionList is not List."
        paths = {}
        # paths = []
        connectionList = self.db.getOrderedConnections()
        graph = tools.dumpConnectionsToGraph(connectionList, self.excluded_cities)

        for direction in directionList:
            src_iata = direction.split("-")[0]
            dst_iata = direction.split("-")[1]
            paths[direction] = BFS(graph, self.search_depth, src_iata, dst_iata)

        # for src_iata in self.departure_cities:
        #     for dst_iata in self.arrival_cities:
        #         k = "{}-{}".format(src_iata, dst_iata)
        #         paths[k] = BFS(graph, self.search_depth, src_iata, dst_iata)
        #         # paths.extend(BFS(graph, self.search_depth, src_iata, dst_iata))

        if lm.enabled():
            with open(os.path.join(self.log_dir, "connectionsTree.txt"),'w') as f:
                json.dump(paths, f, cls=tools.FLJsonEncoder, indent=4)
            f.close()

            with open(os.path.join(self.log_dir, "graph.txt"),'w') as f:
                json.dump(graph, f, cls=tools.FLJsonEncoder, indent=4)
            f.close()

        return paths, connectionList

    def getConfigurationDates(self, newsletterData):
        end_date = datetime.date.min
        start_date = datetime.date.max

        for trip in newsletterData:
            for key, config in trip.items():
                # for config in value['config']:
                if config['start'] > datetime.date.today() and config['start'] < start_date:
                    start_date = config['start']

                if config['end'] > end_date:
                    end_date = config['end']
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time())
        return (start_date, end_date)

    def getScheduleConfiguration(self, newsletterData):
        """TODO: Docstring for getScheduleConfiguration.
        :returns: TODO

        """
        use_newsletterDates = True
        if use_newsletterDates:
            date_from, date_to = self.getConfigurationDates(newsletterData)
        else:
            month_delta = int(self.cfg['FLIGHT_SEARCH']['month_delta'])
            delay_data = datetime.timedelta(days=7)
            date_from = datetime.datetime.now() + delay_data;
            date_to = date_from + monthdelta(month_delta)

        config = {  }
        config['date_from'] = date_from
        config['date_to'] = date_to

        return config

    def removeEmptyFlights(self, scheduledFlightSuite):
        """TODO: Docstring for removeEmptyFlights.

        :scheduledFlightSuite: TODO
        :returns: TODO

        """
        if type(scheduledFlightSuite) is not list:
            raise TypeError
        # newScheduledFlightSuite = copy.deepcopy(scheduledFlightSuite)

        for trip in scheduledFlightSuite:
            for flightSuiteName, flightSuiteList in trip.items():
                for directionKey, directionList in flightSuiteList.items():
                    directionList[:] = [ direction for direction in directionList if len(direction[ list(direction.keys())[0] ]) > 0 ]
                        # for flightName, flightList in direction.items():
                        #     if len(flightList) == 0:
                        #         del scheduledFlightSuite[i][flightSuiteName][directionKey][j]
                    # else:
                    #     for i, direction in enumerate(flightList):
                    #         for k, v in direction.items():
                    #             if type(v) is list and len(v) == 0:
                    #                 newScheduledFlightSuite[flightSuiteName][flightName].remove(i)
                    #                 continue

        return scheduledFlightSuite

    def calculateCosts(self, scheduledFlightSuite):
        """TODO: Docstring for calculateCosts.

        :scheduledFlightSuite: TODO
        :returns: TODO

        """
        # newScheduledFlightSuite = copy.deepcopy(scheduledFlightSuite)
        currencyCache = {
            self.currencyProvider.baseCurrencySymbol: 1,
            "BAM" : 0.46,
            "RSD" : 29.16,
            "MKD" : 14.50
        }

        for trip in scheduledFlightSuite:
            for flightSuiteName, flightSuiteList in trip.items():
                for directionKey, directionList in flightSuiteList.items():
                    for direction in directionList:
                        for flightName, flightList in direction.items():
                            for direction in flightList:
                                    fastestCalc = 0
                                    cheapestCalc = 0
                                    cheapest_departDateTime = 0
                                    cheapest_arrivalDateTime = 0
                                    for k, v in direction.items():
                                        if type(v) is list:
                                            currencySymbol = v[0].currency
                                            if currencySymbol in currencyCache:
                                                currencyRate = currencyCache[currencySymbol]
                                            else:
                                                currencyRate = \
                                                self.currencyProvider.getCurrencyExchangeRate(currencySymbol)[currencySymbol]
                                                currencyCache[currencySymbol] = currencyRate
                                            
                                            fastestCalc += v[0].price/currencyRate
                                            tmpList = [ elem.price for elem in v ]
                                            idx = tmpList.index(min(tmpList))
                                            cheapestCalc += v[idx].price/currencyRate
                                    direction['fastestTotalCost'] = round(fastestCalc, 2)
                                    direction['cheapestTotalCost'] = round(cheapestCalc, 2)

        return scheduledFlightSuite

    def __isDirectionConsistent(self, direction):
        """TODO: Docstring for __checkDirection.
        :returns: TODO

        """
        for k, v in direction.items():
            if type(v) is list and len(v) == 0:
                return False
        return True

    def dumpToFile(self, fileName, data):
        """TODO: Docstring for dumpToFile.

        :fileName: TODO
        :returns: TODO

        """
        if lm.dump_files():
            with open(os.path.join(self.log_dir, fileName),'w') as f:
                json.dump(data, f, cls=tools.FLJsonEncoder, indent=4)
            f.close()

    def getDefaultConfig(self):
        defaultConfig = [ {
            'mode': 0,
            'start': datetime.date(2017, 5, 15),
            'end': datetime.date.max,
            'days': 5
        },
        {
            'mode': 1,
            'start': datetime.date(2017, 5, 5),
            'time_start': datetime.time(12,0,0),
            'end': datetime.date(2017, 6, 30),
            'time_end': datetime.time(8,0,0),
            'days': 5
        },
        {
            'mode': 2,
            'start': datetime.date(2017, 5, 5),
            'time_start': datetime.time(12,0,0),
            'end': datetime.date(2017, 6, 30),
            'time_end': datetime.time(8,0,0),
            'days': 5
        }
        ]

        return { 'default': defaultConfig[1] }

    def filterFlightPack(self, flightSuiteList, configList):
        """TODO: Docstring for filterFlightPack.

        :flightSuiteList: TODO
        :configList: TODO
        :returns: TODO

        """
        filteredFlightPack = {}
        for flightSuiteName, flightSuite in flightSuiteList.items():
            if flightSuiteName in configList:
                configs = configList[flightSuiteName]
            else:
                configs = [configList['default']]

            lst = []
            for config in configs['configs']:
                lst.append({ 'config': config, 'flights': self.filterFlights(flightSuiteName, flightSuite, config) })
            filteredFlightPack[flightSuiteName] = lst #{ 'config': config, 'flights': self.filterFlights(flightSuiteName, flightSuite, config) }

        return filteredFlightPack

    def findCheapFlights(self, flightDetails):
        pass


    def filterFlights(self, direction, flightSuite, scheduleDetails = { 'mode': 0, 'start': datetime.date.today, 'end':
                                                            datetime.datetime.today(), 'days': 5 } ):
        """TODO: Docstring for filterFlights.
        :returns: list of {'to': flight, 'from': flight}

        """
        options = {
            # exact date and length
            0: self.__scheduleMode0,
            1: self.__scheduleMode1,
            2: self.__scheduleMode2,
            3: self.__scheduleMode3,
            4: self.__scheduleMode4
        }
        toList, backList = self.flse.splitFlight(direction, flightSuite)
        return options[scheduleDetails['mode']](direction, flightSuite, scheduleDetails, toList, backList)

    def __scheduleMode0(self, direction, flightSuite, config, toList, backList): # schedule flight in exact date and length
        # self.dumpToFile("{}_toList.txt".format(direction), toList)
        # self.dumpToFile("{}_backList.txt".format(direction), backList)
        config['end'] = config['start'] + datetime.timedelta(days=int(config['days']))
        result = self.flse.findFlights(toList, backList, config)
        return result

    def __scheduleMode1(self, direction, flightSuite, config, toList, backList): # schedule all flights during weekend
        # toList, backList = self.flse.splitFlight(direction, flightSuite)
        weekendList = [ ]
        afterWeekend = datetime.timedelta(days=3)
        day = datetime.timedelta(days=1)
        week = datetime.timedelta(days=7)
        date = config['start']

        while date <= config['end']:
            if date.weekday() == 4:
                weekendList.append([date, date + afterWeekend])
                date = date + week
            else:
                date = date + day

        result = self.flse.findWeekendFlights(toList, backList, config, weekendList)
        return result

    def __scheduleMode2(self, direction, flightSuite, config, toList, backList): # schedule 4-day flights with weekends
        # toList, backList = self.flse.splitFlight(direction, flightSuite)
        weekendList = [ ]
        afterWeekend = datetime.timedelta(days=4)
        day = datetime.timedelta(days=1)
        week = datetime.timedelta(days=7)
        date = config['start']
        while date <= config['end']:
            if date.weekday() in [2, 3]:
                weekendList.append([date, date + afterWeekend])
            date = date + day

        result = self.flse.findWeekendFlights(toList, backList, config, weekendList)
        return result

    def __scheduleMode3(self, direction, flightSuite, config): # schedule flight including weekend and length
        pass

    def __scheduleMode4(self, direction, flightSuite, config): # not specified
        pass
