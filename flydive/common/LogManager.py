import logging
import logging.config
import os.path
from common.ConfigurationManager import CfgMgr

logHandler=None

def init(dirname='configs', configFileName="logger.cfg"):
    _configFileName = configFileName
    _dirname = dirname

    global logHandler
    logging.config.fileConfig(os.path.join('.', _dirname, _configFileName))
    logHandler = logging.getLogger('default')

def debug(log):
    """TODO: Docstring for getLogger.

    :module: TODO
    :returns: TODO

    """
    if CfgMgr().getConfig()['LOGGER']['debug'] == 'on':
        logHandler.debug(log)

def exception():
    """TODO: Docstring for getLogger.

    :module: TODO
    :returns: TODO

    """
    if CfgMgr().getConfig()['LOGGER']['debug'] == 'on':
        logHandler.exception("Got exception!")

def enabled():
     return CfgMgr().getConfig()['LOGGER']['debug'] == 'on'

def dump_files():
     return CfgMgr().getConfig()['LOGGER']['debug_files'] == 'on'
