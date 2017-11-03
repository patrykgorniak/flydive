class FLPlugin():
    def __init__(self):
        self.airportsReady = False
        self.connectionsReady = False

    def run(self, fligthTree, connectionList, config):
        assert False, "Base class: not implemented."

    def initAirports(self):
        assert False, "Base class: not implemented."

    def initConnections(self):
        assert False, "Base class: not implemented."

    def getAirlineCode(self):
        assert False, "Base class: not implemented."

