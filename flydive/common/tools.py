import json

def printJSON(JSONObject):
    """TODO: Docstring for printJSON.

    :JSONObject: TODO
    :returns: TODO

    """
    # print(JSONObject)
    print(json.dumps(JSONObject, indent=4, sort_keys=True))
