import requests
import logging
from wizzair.wizzairmanager import WizzairPlugin
from wizzair.commonUrls import CommonData
from common import HttpManager
from common.tools import printJSON
from common.ConfigurationManager import CfgMgr
from common import LogManager as LogMgr
from FLPluginManager import FLPluginManager


def setupLogger(cfg):
    LogMgr.init(dirname=cfg['config_dir'], configFileName=cfg['config_name'])

def main():
    cfg = CfgMgr().getConfig()
    setupLogger(cfg['LOGGER'])

    flydive = FLPluginManager()
    flydive.registerPlugin(WizzairPlugin)

    flydive.start()

if __name__ == "__main__":
    main()
