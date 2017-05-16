from common import tools
from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from ryanair import RyanairUrls as RyanairData

class RyanairParser():

    """Docstring for RyanairParser. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

    def extractJSONAirportsToList(self, JSONAirports):
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
        airportList = []
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



