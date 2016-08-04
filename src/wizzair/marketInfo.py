import re
import json

def getAirports(httpContent):
    """Parser HttpContent and return JSON object with airports

    :httpContent: TODO
    :returns: TODO

    """
    airports = re.findall(r'wizzAutocomplete.STATION.*?=\s*(.*?);', httpContent.text, re.DOTALL | re.MULTILINE)
    return json.loads(airports[0])


def getAirportConnections(httpContent):
    """Parse HttpContent and return JSON object with fly connections

    :httpContent: TODO
    :returns: TODO

    """
    connections = re.findall(r'wizzAutocomplete.MARKETINFO.*?=\s*(.*?);', httpContent.text, re.DOTALL | re.MULTILINE)
    return json.loads(connections[0])   

