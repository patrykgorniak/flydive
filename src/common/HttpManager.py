import requests

def getPage(url, params = {}):
    """Downloads page from url using passed params

    :url: TODO
    :params: TODO
    :returns: 

    """
    r = requests.get(url)
    if (r.status_code == requests.codes.ok):
        return r;
    else:
        return None
