import requests
import time

def getMethod(url, params = {}):
    """Downloads page from url using passed params

    :url: TODO
    :params: TODO
    :returns:

    """
    r = requests.get(url)
    if (r.status_code == requests.codes.ok):
        return r;
    else:
        raise AssertionError('Post method error!')
        return None

def postMethod(url, json_data = {}):
    """Downloads page from url using passed params

    :url: TODO
    :params: TODO
    :returns:

    """

    r = requests.post(url, json = json_data)
    if (r.status_code == requests.codes.ok):
        return r;
    else:
        time.sleep(60)
        r = requests.post(url, json = json_data)
        if (r.status_code == requests.codes.ok):
            return r;
        else:
            raise AssertionError('Post method error!')
            return None
