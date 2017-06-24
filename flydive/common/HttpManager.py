import requests
from common import LogManager as lm
import time

def debug(msg):
    lm.debug("HttpManager: {0}".format(msg))
    
def getMethod(url, params = {}, proxy = {}):
    r = requests.get(url, proxies = proxy)

    if (r.status_code == requests.codes.ok):
        return r;
    time.sleep(1)

    return None

def postMethod(url, json_data = {}, proxy = {}):
    r = requests.post(url, json = json_data, proxies = proxy)
    if (r.status_code == requests.codes.ok):
        return r;
    time.sleep(1)

    return None
