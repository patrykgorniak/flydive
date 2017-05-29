from common import tools
from common.tools import TimeTable
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from ryanair import RyanairUrls as RyanairData
import calendar
import datetime

class RyanairParser():

    """Docstring for RyanairParser. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

    def handleAirportException(self, airport):
        if airport['iataCode']=="EZE":
            return Airport(iata=airport['iataCode'],
                              name=airport['name'],
                              latitude=-airport['coordinates']['latitude'],
                              longitude=airport['coordinates']['longitude']
                              )
        elif airport['iataCode']=="ASU":
            return Airport(iata=airport['iataCode'],
                              name=airport['name'],
                              latitude=-airport['coordinates']['latitude'],
                              longitude=-airport['coordinates']['longitude']
                              )
        elif airport['iataCode']=="CCS":
            return Airport(iata=airport['iataCode'],
                              name=airport['name'],
                              latitude=-airport['coordinates']['latitude'],
                              longitude=-airport['coordinates']['longitude']
                              )
        elif airport['iataCode']=="JFK":
            return Airport(iata=airport['iataCode'],
                              name=airport['name'],
                              latitude=airport['coordinates']['latitude'],
                              longitude=-airport['coordinates']['longitude']
                              )

    def extractJSONAirportsToList(self, JSONAirports):
        useNew = True
        """
        Dicts of dicts:
            {
            "IATA": {
                "name": "airport name",
                "country": "country code",
                "timeZone": "timezone code",
                "latitude": "432435N",
                "longitude": "00923423E"
                }
            }
        """
        exceptionList = [ "EZE", "ASU", "CCS", "JFK" ]

        airportList = []
        if useNew == True:
            for airport in JSONAirports:
                if airport['iataCode'] in exceptionList:
                    airport = self.handleAirportException(airport)
                else:
                    airport = Airport(iata=airport['iataCode'],
                                      name=airport['name'],
                                      latitude=airport['coordinates']['latitude'],
                                      longitude=airport['coordinates']['longitude']
                                      )
                airportList.append(airport)
        else:
            for IATA, details in JSONAirports.items():
                lat, long = tools.dms_to_dd_conv(details['latitude'], details['longitude'])
                airport = Airport(iata=IATA,
                                  name=details['name'],
                                  latitude=lat,
                                  longitude=long
                                  )
                airportList.append(airport)
        return airportList

    def extractJSONConnectionToList(self, connections):
        connectionList = []
        DS = connections['iataCode']
        for route in connections['routes']:
            route_split = route.split(':')
            if route_split[0]=='airport':
                connection = Connections(src_iata = DS,
                                         dst_iata = route_split[1],
                                         carrierCode = RyanairData.carrierCode
                                         )
                connectionList.append(connection)
        return connectionList

    def extractJSONTimeTable(self, JSONTimeTable, flightDetails):
        if not JSONTimeTable['outbound']['minFare']:
            return []

        timeTableList = []
        lastDayInMonth =  calendar.monthrange(flightDetails['year'], flightDetails['month'])[1]
        for day in range(1, lastDayInMonth, 6):
            timeTable = \
            TimeTable(flightDetails['src_iata'], flightDetails['dst_iata'], datetime.datetime(flightDetails['year'],
                                                                                              flightDetails['month'],
                                                                                              day))
            timeTableList.append(timeTable)

        return timeTableList

    def extractJSONFlightDetails(self, flightDetailsJSON):
        flightDetailsList = []

        currencyCode = flightDetailsJSON['currency']

        for trip in  flightDetailsJSON['trips']:
            # depDate = flight['departureDateTime']
            # arrDate = flight['arrivalDateTime']
            depStation = trip['origin']
            arrStation = trip['destination']
            for date in trip['dates']:
                for flight in date['flights']:

                    if flight['faresLeft'] == 0: # All seats were sold out
                        continue

                    depDate = flight['time'][0]
                    arrDate = flight['time'][1]
                    flightNb = flight['flightNumber']
                    price_amount = flight['regularFare']['fares'][0]['amount']
                    flightDetails = FlightDetails(departure_DateTime = datetime.datetime.strptime(depDate, "%Y-%m-%dT%H:%M:%S.000"), 
                                                  arrival_DateTime = datetime.datetime.strptime(arrDate, "%Y-%m-%dT%H:%M:%S.000"),
                                                  price = price_amount,
                                                  flightNumber = flightNb,
                                                  currency = currencyCode,
                                                  isMacStation = False,
                                                  isAirportChanged = False,
                                                  inDC = True,
                                                  src_iata = depStation,
                                                  dst_iata = arrStation,
                                                  availableCount = flight['infantsLeft']
                                                  )
                    flightDetailsList.append(flightDetails)

        return flightDetailsList
