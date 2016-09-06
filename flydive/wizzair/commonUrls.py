from enum import Enum

class CommonData(Enum):
    AIRPORTS = "https://cdn.static.wizzair.com/pl-PL/Markets.js"
    TimeTable = "https://cdn.static.wizzair.com/pl-PL/TimeTableAjax?departureIATA={0}&arrivalIATA={1}&year={2}&month={3}"

