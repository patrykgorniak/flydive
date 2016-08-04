import requests

def getPage(url, params = {}):
    """Downloads page from url using passed params

    :url: TODO
    :params: TODO
    :returns: 

    """
    return requests.get(url)
