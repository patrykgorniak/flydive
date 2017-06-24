import datetime
from common import LogManager as lm
from common.ConfigurationManager import CfgMgr

class FLSearchEngine():

    """Docstring for FDSearchEngine. """

    def __init__(self):
        """TODO: to be defined1. """
        self.global_cfg = CfgMgr().getConfig()

    def log(self, message):
        lm.debug("FLSearchEngine: {0}".format(message))

    def __build_tree(self, scheduledFlights, previousFlight, flightList, lastFlight, flightDetailList, criteria):
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
        scheduledFlights['departure_DateTime'] = previousFlight.departure_DateTime
        flightTime = previousFlight.arrival_DateTime - previousFlight.departure_DateTime

        for flightChange in flightList:
            scheduledFlights[flightChange] = self.__findFlight(previousFlight, flightDetailList[flightChange], criteria)
            if len(scheduledFlights[flightChange]) > 0:
                flightTime = flightTime + scheduledFlights[flightChange][0].arrival_DateTime - scheduledFlights[flightChange][0].departure_DateTime

            if len(scheduledFlights[flightChange]) == 0: # No flights were found from flightChange, mark flight as invalid
                scheduledFlights[flightChange] = self.__findFlight(previousFlight, flightDetailList[flightChange], {'time_change_min': 2, 'time_change_max': 72 })
                scheduledFlights['s'] = 0

                # calculate flight time
                if len(scheduledFlights[flightChange]) > 0:
                    flightTime = flightTime + scheduledFlights[flightChange][0].arrival_DateTime - scheduledFlights[flightChange][0].departure_DateTime

                if len(scheduledFlights[flightChange]) > 0 :
                    previousFlight = scheduledFlights[flightChange][0]
            else:
                previousFlight = scheduledFlights[flightChange][0]

            if len(scheduledFlights[flightChange]) == 0:
                return None

        scheduledFlights['arrival_DateTime'] = scheduledFlights[lastFlight][0].arrival_DateTime

        scheduledFlights['flightTime'] = round(flightTime.total_seconds()/(60*60), 2)
        return scheduledFlights

    def __findFlight(self, previousFlight, flightDetails, criteria):
        """TODO: Docstring for findFlight.

        :flightFrom: TODO
        :next_airport_key: TODO
        :flightDetails: TODO
        :criteria: TODO
        :returns: List of flights

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
        # self.log(airportList)
        scheduledFlights = []

        for start_flight in flightDetails[airportList[0]]:
            scheduled = {}
            scheduled[airportList[0]] = [start_flight]
            flightTree = self.__build_tree(scheduled, start_flight, airportList[1:], airportList[-1], flightDetails, criteria )
            if flightTree is not None:
                scheduledFlights.append(flightTree)

        return scheduledFlights #self.__validateData(scheduledFlights)

    def __validateData(self, scheduledFlights):
        """TODO: Docstring for __validateData.

        :scheduledFlight: TODO
        :returns: TODO

        """
        for flight in scheduledFlights:
            flight['s'] = 1
            for changeName, changeList in flight.items():
                if type(changeList) is list and len(changeList) == 0:
                    flight['s'] = 0
                    break

        return scheduledFlights

    def splitFlight(self, direction, flightSuite):
        """TODO: Docstring for splitFlight.

        :flightSuite: TODO
        :returns: TODO

        """
        startFrom = direction.split("-")[0]
        toList = {}
        backList = {}
        for flightDirection, flightList in flightSuite.items():
            if flightDirection.split("-")[0] == startFrom:
                toList[flightDirection] = flightList
            else:
                backList[flightDirection] = flightList

        return toList, backList

    def findFlights(self, toFlightList, fromFlightList, config):
        """TODO: Docstring for findFlights.

        :toFlightList: TODO
        :fromFlightList: TODO
        :config: TODO
        :returns: TODO

        """
        departFlight = []
        returnFlight = []
        max_change_time = config['max_change_time'] #int(self.global_cfg['FLIGHT_SEARCH']['max_flight_change_timeH'])
        flex_time = config['flex_time']             #int(self.global_cfg['FLIGHT_SEARCH']['flex_time'])

        start_date = datetime.datetime.combine(config['start'], config['time_start'])
        back_date = datetime.datetime.combine(config['end'], config['time_end'])

        for flightSuite in toFlightList:
            for flightName, flightList  in flightSuite.items():
               tmp = [x for x in flightList if (
                   x['arrival_DateTime'] - x['departure_DateTime'] <= datetime.timedelta(hours = max_change_time + x['flightTime']) and
                   x['departure_DateTime'] >= start_date and
                   x['departure_DateTime'] <= start_date + datetime.timedelta(days=flex_time)
               ) ]
    
               if len(tmp) > 0:
                   departFlight.append({flightName: tmp})

        for flightSuite in fromFlightList:
            for flightName, flightList  in flightSuite.items():
               tmp = [x for x in flightList if (
                   x['arrival_DateTime'] - x['departure_DateTime'] <= datetime.timedelta(hours = max_change_time + x['flightTime']) and
                   x['arrival_DateTime'] >= back_date - datetime.timedelta(days=flex_time) and
                   x['arrival_DateTime'] <= back_date
               ) ]
    
               if len(tmp) > 0:
                   returnFlight.append({ flightName: tmp })

        return {'DEP': departFlight, 'RET': returnFlight}

    def findWeekendFlights(self, toFlightList, fromFlightList, config, weekendList):
        """TODO: Docstring for findFlights.

        :toFlightList: TODO
        :fromFlightList: TODO
        :config: TODO
        :returns: TODO

        """
        max_change_time = config['max_change_time'] #int(self.global_cfg['FLIGHT_SEARCH']['max_flight_change_timeH'])
        flex_time = config['flex_time']             #int(self.global_cfg['FLIGHT_SEARCH']['flex_time'])

        departFlight = []
        arrivalFlight = []

        list = []
        for weekend in weekendList:
            l1 = []
            l2 = []
            tmpFlightList = { 'w': weekend }
            start_date = datetime.datetime.combine(weekend[0], config['time_start'])
            back_date = datetime.datetime.combine(weekend[1], config['time_end'])

            for flightSuite in toFlightList:
                for (toFlightName, flightList) in flightSuite.items():
                    toFlights= [x for x in flightList if (
                        x['arrival_DateTime'] - x['departure_DateTime'] <= datetime.timedelta(hours = max_change_time + x['flightTime']) and
                        x['departure_DateTime'].date() >= start_date.date() and x['departure_DateTime'].date() <= start_date.date() +
                        datetime.timedelta(days = flex_time)
                    )]

                    if len(toFlights) > 0:
                        l1.append({toFlightName: toFlights})

            for flightSuite in fromFlightList:
                for (fromFlightName, flightList) in flightSuite.items():
                    fromFlights = [x for x in flightList if (
                        x['arrival_DateTime'] - x['departure_DateTime'] <= datetime.timedelta(hours = max_change_time + x['flightTime']) and
                        x['arrival_DateTime'].date() >= back_date.date() - datetime.timedelta(days = flex_time) and x['arrival_DateTime'].date() <= back_date.date()
                    )]
                    if len(fromFlights) > 0:
                        l2.append({fromFlightName: fromFlights})

            if len(l1) > 0 and len(l2) > 0:
                tmpFlightList['DEP'] = l1
                tmpFlightList['RET'] = l2
            else:
                tmpFlightList['DEP'] = None
                tmpFlightList['RET'] = None

            list.append(tmpFlightList)

        return list
