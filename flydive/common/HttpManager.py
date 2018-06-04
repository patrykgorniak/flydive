from ratelimit import limits, sleep_and_retry
import requests
from common import LogManager as lm
import time

def debug(msg):
    lm.debug("HttpManager: {0}".format(msg))

@sleep_and_retry
@limits(calls=170, period=60)
def getMethod(url,  params = {}, proxy = {}, headers = {}, tries = 0):
    counter = 0
    while True:
        r = requests.get(url)#, proxies = proxy, headers=headers)
    
        if (r.status_code == requests.codes.ok):
            return r;
        counter += 1
        time.sleep( counter * 2)
        if counter > tries:
            break
    
    debug("Url get method: " + url)
    return None

@sleep_and_retry
@limits(calls=200, period=60)
def postMethod(url, json_data = {}, proxy = {}):
    r = requests.post(url, json = json_data)#, proxies = proxy)
    if (r.status_code == requests.codes.ok):
        return r;
    debug("Url post method: " + url)
    time.sleep(1)

    return None
