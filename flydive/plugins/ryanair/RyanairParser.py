from common import tools
from common.tools import TimeTable
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from plugins.ryanair import RyanairUrls as RyanairData
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
                                      longitude=airport['coordinates']['longitude'],
                                      country_code=airport['countryCode'],
                                      currency_code=airport['currencyCode'],
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

    def extractJSONConnectionToList(self, connectionJSON):
        connectionList = []
        
        for c in connectionJSON:
#             if c['connectingAirport']:
#                 continue
            connectionList.append(Connections(src_iata = c['airportFrom'],
                                             dst_iata = c['airportTo'],
                                             carrierCode = RyanairData.carrierCode
                                             )
                                  )
        
#         
#         for connectionsFromAirport in connections:
#             DS = connectionsFromAirport['iataCode']
#             for route in connections['routes']:
#                 route_split = route.split(':')
#                 if route_split[0]=='airport':
#                     connection = Connections(src_iata = DS,
#                                              dst_iata = route_split[1],
#                                              carrierCode = RyanairData.carrierCode
#                                              )
#                     connectionList.append(connection)
        return connectionList

    def extractJSONTimeTable(self, JSONTimeTable, flightDetails):
        assert len(JSONTimeTable['from']) == len(JSONTimeTable['to'])

        timeTableList = []
        for flight in JSONTimeTable['from']:
            timeTable = TimeTable(flightDetails['src_iata'], flightDetails['dst_iata'], datetime.datetime.strptime(flight,'%Y-%m-%d'))
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
