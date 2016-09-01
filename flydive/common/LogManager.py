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