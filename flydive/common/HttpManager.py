import requests
import time

def getMethod(url, params = {}, proxy = {}):

    for i in range(5):
        r = requests.get(url, proxies = proxy)
        if (r.status_code == requests.codes.ok):
            return r;
        time.sleep(60)

    raise AssertionError('Post method error!')
    return None

def postMethod(url, json_data = {}, proxy = {}):
    
    for i in range(5):
        r = requests.post(url, json = json_data, proxies = proxy)
        if (r.status_code == requests.codes.ok):
            return r;
        time.sleep(60)

    raise AssertionError('Post method error!')
    return None
