import datetime
from monthdelta import monthdelta
import requests
import time

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


def main():

    for FROM, TO in airports.items():
        for i in range(MAX_MONTHS):
            date = now + monthdelta(i)
            url = \
            'https://cdn.static.wizzair.com/pl-PL/TimeTableAjax?departureIATA={0}&arrivalIATA={1}&year={2}&month={3}'.format(FROM,
                                                                                                                         TO,
                                                                                                                         date.year,
                                                                                                                         date.month)
            print("Downloading: {0}".format(url))
            data = fetchData(url)
            with open('../tests/wizzair/testdata/{0}_{1}_{2}_{3}.json'.format(FROM, TO, date.month, date.year), 'w') as file:
                file.write(data)
            file.close()
            time.sleep(1)

if __name__=='__main__':
    main()
