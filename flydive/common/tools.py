import json
import datetime
from common.DatabaseModel import *

class TimeTable:
    """docstring for TimeTable"""
    src = ""
    dst = ""
    def __init__(self, src, dst, date):
        self.src = src
        self.dst = dst
        self.date = date

    def __str__(self):
        """TODO: Docstring for __str__.
        :returns: TODO

        """
        return "TimeTable: from: {0} to: {1} date: {2}".format(self.src, self.dst, self.date)

def printJSON(JSONObject):
    """TODO: Docstring for printJSON.

    :JSONObject: TODO
    :returns: TODO

    """
    # print(JSONObject)
    print(json.dumps(JSONObject, indent=4, sort_keys=True))

def str2Boolean(str_data):
    """Converts string to boolean

    :str: Given string
    :returns: Boolean value

    """
    pattern = ['yes', 'true', '1']
    return True if str(str_data).lower() in pattern else False


def dumpConnectionsToGraph(connectionsList, excluded_cities):
    graph = {}
    if type(connectionsList) is list:
        if len(connectionsList) and isinstance(connectionsList[0], Connections):
            for connection in connectionsList:
                if connection.src_iata not in graph:
                    graph[connection.src_iata] = [connection.dst_iata]
                else:
                    graph[connection.src_iata].append(connection.dst_iata)
        else:
            for fromIATA in connectionsList:
                if fromIATA['DS'] in excluded_cities:
                    continue
                dest = []
                for ASL in fromIATA['ASL']:
                    if ASL['SC'] in excluded_cities:
                        continue
                    dest.append(ASL['SC'])
                graph[fromIATA['DS']] = dest
    # file = open("dump_2.txt", 'w')
    # data = "graph = {}".format(str(graph))
    # file.write(data)
    # file.close()
    return graph

def dms_to_dd_conv(dms_lat, dms_long):
     lat_symbol = dms_lat[-1]
     lat_sec = int(dms_lat[-3:-1])
     lat_min = int(dms_lat[-5:-3])
     lat_hour = int(dms_lat[0:-5])
     conv_lat = lat_hour + lat_min/60 + lat_sec/3600

     long_symbol = dms_long[-1]
     long_sec = int(dms_long[-3:-1])
     long_min = int(dms_long[-5:-3])
     long_hour = int(dms_long[0:-5])

     conf_lat = lat_hour + lat_min/60 + lat_sec/3600
     conv_long = long_hour + long_min/60 + long_sec/3600

     dd_lat = conv_lat if lat_symbol=='N' else -conv_lat
     dd_long = conv_long if long_symbol=='E' else -conv_long
     return dd_lat, dd_long

class FLJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, FlightDetails):
            return obj.to_dict()

        if isinstance(obj, datetime.datetime):
            return str(obj)

        if isinstance(obj, datetime.date):
            return str(obj)

        if isinstance(obj, datetime.time):
            return str(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
