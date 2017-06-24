import logging
import logging.config
import os.path
from common.ConfigurationManager import CfgMgr

logHandler=None
_debug_files=None

def init(dump_files, dirname='configs', configFileName="logger.cfg"):
    _configFileName = configFileName
    _dirname = dirname

    global _debug_files
    _debug_files = dump_files
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
     return CfgMgr().getConfig()['LOGGER']['debug_files'] == 'on' or _debug_files
