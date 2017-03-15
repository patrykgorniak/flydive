import json

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


def dumpConnectionsToGraph(connections, excluded_cities):
    graph = {}
    for fromIATA in connections:
        if fromIATA['DS'] in excluded_cities:
            continue
        dest = []
        for ASL in fromIATA['ASL']:
            if ASL['SC'] in excluded_cities:
                continue
            dest.append(ASL['SC'])
        graph[fromIATA['DS']] = dest
    return graph

    file = open("dump.txt", 'w')
    data = "graph = {}".format(str(graph))
    file.write(data)
    file.close()
