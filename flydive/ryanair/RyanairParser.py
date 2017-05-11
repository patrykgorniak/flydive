class RyanairParser():

    """Docstring for RyanairParser. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

    def extractJSONAirportsToList(self, JSONAirports):
        """
        Dicts of dicts:
            {
            "IATA": {
                "name": "airport name",
                "country": "country code",
                "timeZone": "timezone code",
                "latitude": "432435N",
                "longitude": "00923423E"
                }
            }
        """
        airportList = []
        for IATA, details in JSONAirports.items():
            lat = (details['latitude'][:-1])[4:]
            airport = Airport(iata=IATA,
                              name=details['name'],
                              latitude=details['latitude'][:-1],
                              longitude=details['longitude']
                              )
            airportList.append(airport)

