import json
import datetime, time
from plugins.ryanair import RyanairUrls as RyanairData
from common import HttpManager as HttpMgr

class RyanairDl():

    """Docstring for RyanairDl. """

    def __init__(self):
        self.apikey = ""
        self.s_iata = ""
        self.d_iata = ""
        self.date = datetime.date.min


    def getAirports(self):
        url = self.__attachCredentials(RyanairData.CommonData.AIRPORTS)
        airports_text = self.getData(url) #HttpMgr.getMethod(url, tries = 10).text
        json_data = json.loads(airports_text)
        return json_data

    def getConnections(self):
        url = self.__attachCredentials(RyanairData.CommonData.CONNECTIONS)
        connections_text = self.getData(url) #HttpMgr.getMethod(url, tries = 10).text
        json_data = json.loads(connections_text)
        return json_data

    def getTimeTable(self, details = { "src_iata": "", "dst_iata":"", "year":"", "month":"", 'day': "" }):

        src_iata = details['src_iata']
        dst_iata = details['dst_iata']
        
        if [src_iata, dst_iata] == [self.s_iata, self.d_iata]:
            return self.timetable
        # year = details['year']
        # month = details['month']

        # TODO: handle invalid request ex. https://api.ryanair.com/farefinder/3/roundTripFares/WRO/BLQ/cheapestPerDay?outboundMonthOfDate=2017-5-01&market=pl-pl
        url = self.__attachCredentials(RyanairData.CommonData.TimeTable)
        url_from = url.format(src_iata, dst_iata )
        url_back = url.format(dst_iata, src_iata )

        httpContent_from = self.getData(url_from) #HttpMgr.getMethod(url_from, tries = 10).text
        httpContent_to = self.getData(url_back) #HttpMgr.getMethod(url_back, tries = 10).text

        self.timetable  = { "from": json.loads(httpContent_from), "to": json.loads(httpContent_to) }
        
        self.s_iata = src_iata
        self.d_iata = dst_iata
        
        return self.timetable

    def prepareUrl(self, flight):
        url = RyanairData.CommonData.Search
#         url = self.__attachCredentials(RyanairData.CommonData.Search)
        url = self.__attachCredentials(url.format(flight.src, flight.dst, flight.date.date(), flight.date.date() + datetime.timedelta(days=1)))
        return url

    def __attachCredentials(self, url):
        return url + "apikey={}".format(self.apikey)

    def getFlightDetails(self, url, params = {}, proxy = {}, headers = {}):
        date = datetime.datetime.strptime(url.split('&inboundMonthOfDate')[0][-10:], "%Y-%m-%d").date()
        s_iata = url.split('/')[8]
        d_iata = url.split('/')[9]
        if self.sig == [s_iata, d_iata, date.year, date.month]:
            return self.flightDetails
        
        self.flightDetails = self.getData(url) #HttpMgr.getMethod(url)
        self.sig = [s_iata, d_iata, date.year, date.month]
        
        return self.flightDetails

    def getData(self, url):
        tries = 10
        counter = 0
        while True:
            r = HttpMgr.getMethod(url, tries = 0)
            if (r != None):
                return r.text;
            counter += 1
            time.sleep( counter * 2)
            if counter > tries:
                break
