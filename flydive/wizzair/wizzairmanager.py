from wizzair.wizzairdl import WizzairDl

class WizzairPlugin(object):

    """Docstring for WizzairPlugin. """

    def __init__(self):
        self._dlMgr = WizzairDl()
        """TODO: to be defined1. """
    
    def getConnections(self):
        """TODO: Docstring for getConnections.
        :returns: TODO

        """
        print("getConnections");
        return self._dlMgr.getConnections()

    def getAirports(self):
        """TODO: Docstring for getAirports.

        :returns: TODO

        """
        return self._dlMgr.getAirports()

    def downloadData(self):

        """TODO: Docstring for downloadData.
        :returns: TODO

        """
        pass
