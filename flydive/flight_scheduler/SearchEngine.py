import datetime
from common import LogManager as lm

class FLSearchEngine():

    """Docstring for FDSearchEngine. """

    def __init__(self):
        """TODO: to be defined1. """

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

        for flightChange in flightList:
            scheduledFlights[flightChange] = self.__findFlight(previousFlight, flightDetailList[flightChange], criteria)

            if len(scheduledFlights[flightChange]) == 0: # No flights were found from flightChange, mark flight as invalid
                scheduledFlights['s'] = 0
            else:
                previousFlight = scheduledFlights[flightChange][0]
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
        self.log(airportList)
        scheduledFlights = []

        for start_flight in flightDetails[airportList[0]]:
            scheduled = {}
            scheduled[airportList[0]] = [start_flight]
            scheduledFlights.append(self.__build_tree(scheduled, start_flight, airportList[1:], airportList[-1], flightDetails,
                    criteria ))

        return scheduledFlights #self.__validateData(scheduledFlights)

    def __validateData(self, scheduledFlights):
        """TODO: Docstring for __validateData.

        :scheduledFlight: TODO
        :returns: TODO

        """
        for flight in scheduledFlights:
            flight['Status'] = 1
            for changeName, changeList in flight.items():
                if type(changeList) is list and len(changeList) == 0:
                    flight['Status'] = 0
                    break

        return scheduledFlights
