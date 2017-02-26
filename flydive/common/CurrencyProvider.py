import json
import os

currencyProvider = None

def getCurrencyProvider():
    global currencyProvider

    if currencyProvider is None:
        currencyProvider = CurrencyProvider()
    return currencyProvider

class Currency():
    def __init__(self, code, name, nb):
        self.currencyCode = code
        self.currencyName = name
        self.currencyNumber = nb

    def __str__(self):
        return "CurrencyCode: {}, CurrencyName: {}, CurrencyNumber: {}".format(self.currencyCode, self.currencyName,
                                                                             self.currencyNumber)


class CurrencyProvider:
    def __init__(self):
        self.dir = os.path.dirname(__file__)
        self.file_data = open(os.path.join(self.dir, "currencies.json") ,'r').read()
        self.currency_db = json.loads(self.file_data)

    def getCurrency(self, countryName = None):
        for item in self.currency_db['Currencies']:
            if str(item['CountryName']).find(countryName.upper()) != -1:
                return Currency(item['CurrencyCode'], item['CurrencyName'], item['CurrencyNumber'])
        return Currency("N/A","N/A","N/A")


if __name__ == "__main__":
    tool = getCurrencyProvider()
    print(tool.getCurrency("Poland"))
