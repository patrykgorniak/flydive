import requests
import logging
from wizzair.wizzairmanager import WizzairPlugin
from wizzair.commonUrls import CommonData
from common import HttpManager
from common.tools import printJSON
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr


def setupLogger(cfg):
    LogMgr.init(dirname=cfg['config_dir'], configFileName=cfg['config_name'])
    # LogMgr.init()


def main():
    cfg = CfgMgr().getConfig()
    setupLogger(cfg['LOGGER'])

    wiz = WizzairPlugin();
    wiz.fetchAirports()
   # printJSON(wiz.fetchConnections())


    # httpcontent = HttpManager.getPage(CommonData.AIRPORTS.value)
    # print(marketInfo.getAirports(httpcontent)[0]['ShortName'])

if __name__ == "__main__":
    main()
