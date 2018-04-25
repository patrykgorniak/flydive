from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from plugins.norwegian import Common as CommonData
from interfaces.ParserIface import ParserIface

class NorwegianParser(ParserIface):
    """docstring for NorwegianParser"""
    def __init__(self):
        pass 

    def extractJSONAirportsToList(self, airports):
        airportList = []

        for elem in airports:
            airport = Airport(iata = elem['code'],
                              name = elem['displayName']
                              )
            airportList.append(airport)

        return airportList

    def extractJSONConnectionToList(self, connections):
        connectionList = []

        for iata, directions in connections.items():
            for direction in directions:
                connection = Connections(src_iata = str(iata).upper(),
                                          dst_iata = direction,
                                          carrierCode = CommonData.carrierCode
                                          )

                connectionList.append(connection)
        return connectionList
