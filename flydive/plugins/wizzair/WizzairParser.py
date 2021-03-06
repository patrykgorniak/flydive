from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from datetime import datetime
from plugins.wizzair import commonUrls as WizzData
from common.tools import TimeTable
from common import LogManager as lm

class WizzairParser(object):

    """Docstring for WizzairParser. """

    def __init__(self):
        """TODO: to be defined1. """

    def log(self, message):
        lm.debug("WizzairParser: {0}".format(message))

    def extractJSONConnectionToList(self, JSONConnections):
        """ Extractes plain json connections data and pack into ConnectionList

        :JSONConnections: plain wizzair connections in JSON format
        :returns: list of Connections from common.DatabaseModel

        """
        connectionList = []
        for connectionsFromAirport in JSONConnections:
            for ASL in connectionsFromAirport['ASL']:
                self.log("Parse connection from: {0} to {1}".format(ASL['SC'], connectionsFromAirport['DS']))
                connections = Connections(src_iata=ASL['SC'],
                                          dst_iata = connectionsFromAirport['DS'],
                                          carrierCode = WizzData.carrierCode
                                          )
                connectionList.append(connections)

        return connectionList

    def extractJSONFlightDetails(self, JSONFlightDetails):
        """TODO: Docstring for .

        :arg1: TODO
        :returns: TODO

        """
        flightDetailsList = []

        outboundFlights = JSONFlightDetails['outboundFlights']
        returnFlights = JSONFlightDetails['returnFlights']

        flights = []
        # flights = outboundFlights
        flights.extend(outboundFlights)
        flights.extend(returnFlights)

        for flight in flights:
            depDate = flight['departureDateTime']
            arrDate = flight['arrivalDateTime']
            flightNb = flight['flightNumber']
            depStation = flight['departureStation']
            arrStation = flight['arrivalStation']
            fares = flight['fares']
            for fare in fares:
                if fare['bundle'] == "BASIC":
                    wdc = fare['wdc']
                    price_amount = fare['discountedPrice']['amount']
                    currencyCode = fare['discountedPrice']['currencyCode']
                    flightDetails = FlightDetails(departure_DateTime = datetime.strptime(depDate, "%Y-%m-%dT%H:%M:%S"), 
                                                  arrival_DateTime = datetime.strptime(arrDate, "%Y-%m-%dT%H:%M:%S"),
                                                  price = price_amount,
                                                  flightNumber = flightNb,
                                                  currency = currencyCode,
                                                  isMacStation = False,
                                                  isAirportChanged = False,
                                                  inDC = wdc,
                                                  src_iata = depStation,
                                                  dst_iata = arrStation,
                                                  availableCount = fare['availableCount']
                                                  )
                    flightDetailsList.append(flightDetails)

        return flightDetailsList

    def extractJSONAirportsToList(self, JSONAirports):
        """Extracts JSON data with airports and puts to list of Airport type

        :JSONAirports: Airports in JSON format
        :returns: list of Airports

        """
        airportList = []
        for row in JSONAirports:
            if row is not None:
                airport = Airport(iata=row['IATA'],
                                  name=row['ShortName'],
                                  latitude=row['Latitude'],
                                  longitude=row['Longitude']
                                  )
                airportList.append(airport)

        return airportList

    def extractJSONTimeTable(self, JSONTimeTable, flightDetails):
        """TODO: Docstring for function.

        :JSONTimeTable: TODO
        :returns: TODO

        """
        timeTableList = []
        src_iata = JSONTimeTable['DepartureStationCode']
        dst_iata = JSONTimeTable['ArrivalStationCode']

        for date in JSONTimeTable['Dates']:
            currentdate = datetime.strptime(date,"%Y-%m-%dT%H:%M:%S")
            timeTable = TimeTable(src_iata, dst_iata, currentdate)
            timeTableList.append(timeTable)

        return timeTableList

