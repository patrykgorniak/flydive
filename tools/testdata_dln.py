import datetime
from monthdelta import monthdelta
import requests
import time
import sys
import json

now = datetime.datetime.now()

airports = {
    'GDN':'ABZ',
    'ABZ':'GDN',
    'WAW':'LTN',
    'LTN':'WAW',
    'WRO':'EIN'
}

MAX_MONTHS = 6

def getPage(url, params = {}):
    r = requests.get(url)
    if (r.status_code == requests.codes.ok):
        return r;
    else:
        return None

def fetchData(url):
    page = getPage(url)
    return page.text

def postMethod(url, json_data = {}):
    """Downloads page from url using passed params

    :url: TODO
    :params: TODO
    :returns: 

    """
    print(url)
    print(json_data)
    r = requests.post(url, json = json_data)
    if (r.status_code == requests.codes.ok):
        return r;
    else:
        return None

def getFlightDetailsParams(options = []):
    """TODO: Docstring for getFlightDetails.
    :returns: TODO

    """
    params = {
        'adultCount': 1,
        'infantCount': 0,
        'childCount': 0,
        'wdc': 1,
        'flightList': options
        # [
        #     {
        #         'arrivalStation': options['dst_iata'],
        #         'departureStation': options['src_iata'],
        #         'departureDate': options['date']
        #     }
        # ]
    }

    return params

def getFlightDetails():
    """TODO: Docstring for getFlightDetails.
    :returns: TODO

    """
    Search = "https://be.wizzair.com/3.4.0/Api/search/search"
    options = [
        {'departureDate': '2016-11-13', 'departureStation':'LTN', 'arrivalStation': 'WAW' },
        {'departureDate': '2016-11-13', 'departureStation':'WAW', 'arrivalStation': 'LTN' },
        {'departureDate': '2016-11-13', 'departureStation':'WAW', 'arrivalStation': 'MMX' },
        {'departureDate': '2016-11-13', 'departureStation':'MMX', 'arrivalStation': 'WAW' },
        {'departureDate': '2016-11-13', 'departureStation':'BCN', 'arrivalStation': 'KTW' },
        {'departureDate': '2016-11-13', 'departureStation':'KTW', 'arrivalStation': 'BCN' },
    ]
    params = getFlightDetailsParams(options)
    return postMethod(Search, params).text

def main():

    data = getFlightDetails()
    with open('../tests/wizzair/testdata/test_1.json', 'w') as file:
        file.write(data)
    file.close()

    # for FROM, TO in airports.items():
    #     for i in range(MAX_MONTHS):
    #         date = now + monthdelta(i)
    #         url = \
    #         'https://cdn.static.wizzair.com/pl-PL/TimeTableAjax?departureIATA={0}&arrivalIATA={1}&year={2}&month={3}'.format(FROM,
    #                                                                                                                      TO,
    #                                                                                                                      date.year,
    #                                                                                                                      date.month)
    #         print("Downloading: {0}".format(url))
    #         data = fetchData(url)
    #         with open('../tests/wizzair/testdata/{0}_{1}_{2}_{3}.json'.format(FROM, TO, date.month, date.year), 'w') as file:
    #             file.write(data)
    #         file.close()
    #         time.sleep(1)

if __name__=='__main__':
    main()
