from enum import Enum

class CommonData(Enum):
    AIRPORTS = "https://cdn.static.wizzair.com/pl-PL/Markets.js"
    TimeTable = "https://cdn.static.wizzair.com/pl-PL/TimeTableAjax?departureIATA={0}&arrivalIATA={1}&year={2}&month={3}"
    Search = "https://be.wizzair.com/3.8.0/Api/search/search"

class TimeTable:
    """docstring for TimeTable"""
    src = ""
    dst = ""
    def __init__(self, src, dst, date):
        self.src = src
        self.dst = dst
        self.date = date

    def __str__(self):
        """TODO: Docstring for __str__.
        :returns: TODO

        """
        return "TimeTable: from: {0} to: {1} date: {2}".format(self.src, self.dst, self.date)

carrierCode = 'W6'
airline_name = 'Wizz Air'
