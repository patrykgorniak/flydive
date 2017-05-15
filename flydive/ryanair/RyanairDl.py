import json
from ryanair.RyanairUrls import CommonData

import common.HttpManager as HttpMgr

class RyanairDl():

    """Docstring for RyanairDl. """

    def __init__(self):
        """TODO: to be defined1. """
        pass


    def getAirports(self):
        airports_text = HttpMgr.getMethod(CommonData.AIRPORTS).text
        json_data = json.loads(airports_text)
        return json_data
