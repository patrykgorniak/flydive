class CommonData():
    MAIN = "http://ryanair.com/"
    AIRPORTS = "http://apigateway.ryanair.com/pub/v1/core/3/airports?"
    CONNECTIONS = "http://apigateway.ryanair.com/pub/v1/core/3/routes?"
    TimeTable = "http://apigateway.ryanair.com/pub/v1/timetable/3/schedules/{}/{}/availability?"
    # \
    # "https://api.ryanair.com/farefinder/3/roundTripFares/{}/{}/cheapestPerDay?outboundMonthOfDate={}&market=pl-pl"
#    Search = "https://desktopapps.ryanair.com/v4/pl-pl/availability?ADT=1&CHD=0&Origin={}&Destination={}&DateOut={}&DateIn={}&FlexDaysIn=6&FlexDaysOut=6&INF=0&RoundTrip=true&exists=false&IncludeConnectingFlights=true&toUs=AGREED"
    Search = "http://apigateway.ryanair.com/pub/v1/farefinder/3/roundTripFares/{}/{}/cheapestPerDay?outboundMonthOfDate={}&inboundMonthOfDate={}&"
#     "http://fraas-prod.apigee.net/pub/v1/reservations/AvailabilityV2 
        

carrierCode = 'FR'
airline_name = 'RyanAir'
