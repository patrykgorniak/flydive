class IATADataProvider():

    """Docstring for IATADataProvider. """

    def __init__(self):
        self.path = "../data/airports.dat"

    def loadData(self, path):
        """TODO: Docstring for loadFile.

        :path: TODO
        :returns: TODO

        """
        airportList = {}
        with open(path, 'r', encoding='utf-8') as file:
            airportData = file.readlines()
            for airport in airportData:
                aSplit = airport.replace('"',"").split(',')
                iata = aSplit[4]
                entry = {
                    'name': aSplit[1],
                    'city': aSplit[2],
                    'countryName': aSplit[3],
                    'lat': aSplit[6],
                    'long': aSplit[7]
                }
                airportList[iata] = entry
        return airportList

if __name__ == "__main__":
    iataProvider = IATADataProvider()
    print(iataProvider.loadData("./data/airports.dat"))
    
