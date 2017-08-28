from common import HttpManager
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
        self.baseCurrencySymbol = "PLN"

    def getCurrency(self, countryName = None):
        for item in self.currency_db['Currencies']:
            if str(item['CountryName']).find(countryName.upper()) != -1:
                return Currency(item['CurrencyCode'], item['CurrencyName'], item['CurrencyNumber'])
        return Currency("N/A","N/A","N/A")

    def getCurrencyExchangeRate(self, currencySymbol="", baseCurrencySymbol = "PLN"):
        """TODO: Docstring for getCurrencyRatio.
        :returns: TODO
        """
        url = "http://api.fixer.io/latest?symbols={}&base={}".format(currencySymbol, baseCurrencySymbol)
        url2 = \
        "http://apilayer.net/api/live?access_key=ffa47d756dc89a895e23a7afa65b49b6&currencies={},PLN&format=1".format(currencySymbol)
        resp = HttpManager.getMethod(url)
        if resp is not None:
            json_data = json.loads(resp.text)['rates']
        else:
            resp = HttpManager.getMethod(url2)
            json_data = { currencySymbol: self.parseApiLayer(resp, currencySymbol) }

        return json_data

    def parseApiLayer(self, inputData, currency):
        """TODO: Docstring for parseApiLayer.
        """
        
        json_data = json.loads(inputData.text)
        currencyRate = json_data['quotes']["USD"+currency]
        baseRate = json_data['quotes']["USDPLN"]
        tmp = 1.0/currencyRate
        currencyToPLN = baseRate * tmp
        return 1.0/currencyToPLN

if __name__ == "__main__":
    tool = getCurrencyProvider()
    print(tool.getCurrency("Poland"))
