class FLHtmlGenerator():

    """Docstring for FLHtmlGenerator. """

    def __init__(self):
        """TODO: to be defined1. """
        pass

    def __getHtmlHeader(self):
        return """<!DOCTYPE html>
<html>
<head>
<style>
* {
  box-sizing: border-box;
}

#myInput {
  background-position: 10px 10px;
  background-repeat: no-repeat;
  width: 100%;
  font-size: 16px;
  padding: 12px 20px 12px 40px;
  border: 1px solid #ddd;
  margin-bottom: 12px;
}

#myTable {
  border-collapse: collapse;
  width: 100%;
  border: 1px solid #ddd;
  font-size: 12px;
}

#myTable th {
  text-align: left;
  padding: 12px;
  font-size: 14px;
}

#myTable tr {
  border-bottom: 1px solid #ddd;
}

#myTable tr.header, #myTable tr:hover {
  background-color: #f1f1f1;
}
</style>
</head>
<body>\n"""

    def __getHtmlFooter(self):
        return """</body>
</html>\n"""

    def __getHeader(self, title):
        tableHeader = "<h2>{}</h2>".format(title)
        return tableHeader

    def __getH3Header(self, title):
        tableHeader = "<h3>{}</h3>".format(title)
        return tableHeader

    def __getTableHeader(self, mode):
        tableHeader = """<table id="myTable">
  <tr class="header">
    <th style="width:20%;">Data [ wyjazd - {} ]</th>
    <th style="width:20%;">Ceny [ w przyblizeniu ]</th>
    <th style="width:40%;">Loty</th>
    <th style="width:10%;">Ilosc przesiadek</th>
  </tr>\n""".format(mode)
        return tableHeader

    def __getTableFooter(self):
        return "</table>"

    def __openTableRow(self):
        return "<tr>\n"

    def __closeTableRow(self):
        return "</tr>\n"

    def __insertColumnData(self, data):
        data = "<td>{}</td>\n".format(data)
        return data

    def __insertDates(self, dates):
        dates_str = "Od: {}<br>Do: {}".format(dates[0], dates[1])
        return self.__insertColumnData(dates_str)

    def __insertPrice(self, total_price_dep, total_price_ret, currency):
        price_str = "<b>Suma: {} {}</b><br><br>Wylot: {} {}<br>Powrot: {} {}".format(round(total_price_dep +
                                                                                           total_price_ret, 2), currency,
                                                                          total_price_dep, currency, total_price_ret,
                                                                          currency)
        return self.__insertColumnData( price_str )

    def __insertChanges(self, dep_changes, ret_changes):
        changes_str = "Wylot: {}<br>Powrot: {}".format(dep_changes, ret_changes)
        return self.__insertColumnData(changes_str)

    def __insertFlights(self, dep_flight, ret_flight):
        flight_str = "{}<br>{}".format(dep_flight, ret_flight)
        return self.__insertColumnData( flight_str )

    def generate_html(self, trip):
        html_data = self.__getHtmlHeader()

        for flightSuiteName, flightSuiteList in trip.items():
            if flightSuiteName is not "CONF":
                html_data += self.__getHeader(flightSuiteName)
                if int(trip['CONF']['mode']) == 0:
                    for type in ["cheapest", "fastest"]:
                        type_key_dep = "{}_DEP".format(type)
                        type_key_ret = "{}_RET".format(type)
                        html_data +=self.__getH3Header(type.capitalize())

                        html_data += self.__getTableHeader("fixed date")
                        html_data += self.addFlight(flightSuiteList, type_key_dep, type_key_ret)
                else:
                    for weekend in flightSuiteList:
                        if weekend['RET'] is None:
                            break

                        for type in ["cheapest", "fastest"]:
                            type_key_dep = "{}_DEP".format(type)
                            type_key_ret = "{}_RET".format(type)
                            html_data +=self.__getH3Header(type.capitalize())

                            html_data += self.__getTableHeader("weekend")
                            html_data += self.addFlight(weekend, type_key_dep, type_key_ret)
        html_data += self.__getHtmlFooter()
        return html_data


    def addFlight(self, flightData, type_key_dep, type_key_ret):
        html_data = ""
        for i in range(min(3, len(flightData[type_key_dep]) )):
            if 'w' in flightData:
                dates = flightData['w']
            else:
                dates = [ flightData[type_key_dep][i]['departure_DateTime'],
                          flightData[type_key_ret][i]['arrival_DateTime']
                         ]

            html_data += self.__openTableRow()
            html_data += self.__insertDates(dates)
            dep_changes = len(flightData[type_key_dep][i]['flightList'])
            dep_price = flightData[type_key_dep][i]['price']
            currency = flightData[type_key_dep][i]['currency']
            dep_flights = "Wyloty:<br>\n"
            for i, flight in enumerate(flightData[type_key_dep][i]['flightList']):
                key = list(flight.keys())[0]
                dep_flights += "{} - Linia: {}, Termin: {}, Cena: {}<br>\n".format(key,
                    flight[key].connection.carrierCode,
                    flight[key].departure_DateTime,
                    str(flight[key].price) + " " + flight[key].currency)

            ret_changes = len(flightData[type_key_ret][i]['flightList'])
            ret_price = flightData[type_key_ret][i]['price']
            ret_flights = "Przyloty:<br>\n"
            for i, flight in enumerate(flightData[type_key_ret][i]['flightList']):
                key = list(flight.keys())[0]
                ret_flights += "{} - Linia: {}, Termin: {}, Cena: {}<br>\n".format(key,
                    flight[key].connection.carrierCode,
                    flight[key].departure_DateTime,
                    str(flight[key].price) + " " + flight[key].currency)

            html_data += self.__insertPrice(dep_price, ret_price, currency)
            html_data += self.__insertFlights(dep_flights, ret_flights)
            html_data += self.__insertChanges(dep_changes, ret_changes)
            html_data += self.__closeTableRow()
        html_data += self.__getTableFooter()
        return html_data
