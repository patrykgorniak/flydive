import logging
import logging.config
import os.path

def init(dirname='configs', configFileName="logger.cfg"):
    _configFileName = configFileName
    _dirname = dirname

    logging.config.fileConfig(os.path.join('.', _dirname, _configFileName))
    logger = logging.getLogger('default')
    logger.debug("Logger init.")
