from common.FLPlugin import FLPlugin
from ryanair.RyanairDl import RyanairDl

class RyanairManager(FLPlugin):

    """Docstring for RyanairManager. """

    def __init__(self):
        FLPlugin.__init__(self)
        self.ryanairdl = RyanairDl()

    def run(self, flightTree, connectionList, config):
        """TODO: Docstring for run.

        :flightTree: TODO
        :connectionList: TODO
        :config: TODO
        :returns: TODO

        """
        pass

    def initAirports(self):
        """TODO: Docstring for initAirports.
        :returns: TODO

        """
        self.ryanairdl.getAirports()

    def initConnections(self):
        """TODO: Docstring for initConnections.
        :returns: TODO

        """
        pass
