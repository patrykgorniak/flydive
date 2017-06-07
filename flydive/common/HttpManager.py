import requests
from common import LogManager as lm
import time

def debug(msg):
    lm.debug("HttpManager: {0}".format(msg))
    
def getMethod(url, params = {}, proxy = {}):

    for i in range(2):
        r = requests.get(url, proxies = proxy)
        if (r.status_code == requests.codes.ok):
            return r;
        time.sleep(10)

    debug("URL: {}".format(url))
    debug("PROXY: {} ".format(proxy))
    return None
    raise AssertionError('Post method error!')

def postMethod(url, json_data = {}, proxy = {}):
    
    for i in range(2):
        r = requests.post(url, json = json_data, proxies = proxy)
        if (r.status_code == requests.codes.ok):
            return r;
        time.sleep(10)
    debug("URL: {}".format(url))
    debug("PROXY: {} ".format(proxy))
    return None
    raise AssertionError('Post method error!')
