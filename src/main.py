import requests
from wizzair import marketInfo, commonUrls
from common import HttpManager

def main():
    httpcontent = HttpManager.getPage(commonUrls.COMMON_DATA['AIRPORTS'])
    print(marketInfo.getAirports(httpcontent)[0]['ShortName'])

if __name__ == "__main__":
    main()
