class CommonData():
    MAIN = "http://ryanair.com/"
    AIRPORTS = "https://desktopapps.ryanair.com/v2/pl-pl/res/stations"
    CONNECTIONS = "https://api.ryanair.com/aggregate/3/common?embedded=airports&market=pl-pl"
    TimeTable = \
    "https://api.ryanair.com/farefinder/3/roundTripFares/{}/{}/cheapestPerDay?outboundMonthOfDate={}&market=pl-pl"
    Search = \
    "https://desktopapps.ryanair.com/v3/pl-pl/availability?ADT=1&CHD=0&Origin={}&Destination={}&DateOut={}&DateIn={}&FlexDaysIn=6&FlexDaysOut=6&INF=0&RoundTrip=true&TEEN=0&exists=false&ToUs=AGREED"

carrierCode = 'FR'
airline_name = 'RyanAir'
