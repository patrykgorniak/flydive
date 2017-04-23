import json
import datetime
from common.DatabaseModel import *

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

