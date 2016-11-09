from common.DatabaseModel import Airport, Connections, Airline, FlightDetails
from wizzair import commonUrls as WizzData
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
        for ASL in JSONConnections['ASL']:
            self.log("Parse connection from: {0} to {1}".format(ASL['SC'], JSONConnections['DS']))
            connections = Connections(src_iata=ASL['SC'],
                                      dst_iata = JSONConnections['DS'],
                                      carrierCode = WizzData.carrierCode
                                      )
            connectionList.append(connections)

        return connectionList
