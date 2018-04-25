class DownloadIface():
    def __init__(self):
        pass

    def getFightDetails(self, flight):
        assert False, "Base class: not implemented."

    def packParamsToJSON(self, flight):
        assert False, "Base class: not implemented."

    def getTimeTable(self, details):
        assert False, "Base class: not implemented."

    def getAirports(self):
        assert False, "Base class: not implemented."

    def getConnections(self):
        assert False, "Base class: not implemented."

    def prepareUrl(self, flight):
        assert False, "Base class: not implemented."

    def getFlightDetails(self, url, params = {}, proxy = {}, headers = {}):
        assert False, "Base class: not implemented."
