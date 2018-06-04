class CommonData():
    MAIN = "http://ryanair.com/"
    AIRPORTS = "http://apigateway.ryanair.com/pub/v1/core/3/airports?"
    CONNECTIONS = "http://apigateway.ryanair.com/pub/v1/core/3/routes?"
    TimeTable = "http://apigateway.ryanair.com/pub/v1/timetable/3/schedules/{}/{}/availability?"
    Search ="http://apigateway.ryanair.com/pub/v1/reservations/Availability?ADT=1&CHD=0&Origin={}&Destination={}&DateOut={}&DateIn={}&FlexDaysIn=6&FlexDaysOut=6&RoundTrip=true&toUs=AGREED&"
        

carrierCode = 'FR'
airline_name = 'RyanAir'

REQUESTS_PER_SEC = 50
FlexDays = 6