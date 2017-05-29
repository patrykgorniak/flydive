import json
import datetime
from ryanair import RyanairUrls as RyanairData
from common import HttpManager as HttpMgr

class RyanairDl():

    """Docstring for RyanairDl. """

    def __init__(self):
        """TODO: to be defined1. """
        pass


    def getAirports(self):
        airports_text = HttpMgr.getMethod(RyanairData.CommonData.CONNECTIONS).text
        json_data = json.loads(airports_text)
        return json_data['airports']

    def getConnections(self):
        connections_text = HttpMgr.getMethod(RyanairData.CommonData.CONNECTIONS).text
        json_data = json.loads(connections_text)
        return json_data['airports']

    def getTimeTable(self, details = { "src_iata": "", "dst_iata":"", "year":"", "month":"" }):

        src_iata = details['src_iata']
        dst_iata = details['dst_iata']
        year = details['year']
        month = details['month']

        # TODO: handle invalid request ex. https://api.ryanair.com/farefinder/3/roundTripFares/WRO/BLQ/cheapestPerDay?outboundMonthOfDate=2017-5-01&market=pl-pl
        date = datetime.date(year, month, 1)
        url = RyanairData.CommonData.TimeTable
        url = url.format(src_iata, dst_iata, str(date))

        httpContent = HttpMgr.getMethod(url).text
        return json.loads(httpContent)

    def prepareUrl(self, flight):
        url = RyanairData.CommonData.Search
        url = url.format(flight.src, flight.dst, flight.date, flight.date)
        return url
