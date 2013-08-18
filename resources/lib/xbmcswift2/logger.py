'''
    xbmcswift2.log
    --------------

    This module contains the xbmcswift2 logger as well as a convenience
    method for creating new loggers.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
import logging
from xbmcswift2 import CLI_MODE


# TODO: Add logging to a file as well when on CLI with lowest threshold
#       possible
#fh = logging.FileHandler('log_filename.txt')
#fh.setLevel(logging.DEBUG)
#fh.setFormatter(formatter)
#log.addHandler(fh)
# TODO: Allow a global flag to set logging level when dealing with XBMC
# TODO: Add -q and -v flags to CLI to quiet or enabel more verbose logging


class XBMCFilter(object):
    '''A logging filter that streams to STDOUT or to the xbmc log if
    running inside XBMC.
    '''
    python_to_xbmc = {
        'DEBUG': 'LOGDEBUG',
        'INFO': 'LOGNOTICE',
        'WARNING': 'LOGWARNING',
        'ERROR': 'LOGERROR',
        'CRITICAL': 'LOGSEVERE',
    }

    xbmc_levels = {
        'LOGDEBUG': 0,
        'LOGINFO': 1,
        'LOGNOTICE': 2,
        'LOGWARNING': 3,
        'LOGERROR': 4,
        'LOGSEVERE': 5,
        'LOGFATAL': 6,
        'LOGNONE': 7,
    }

    def __init__(self, prefix):
        self.prefix = prefix

    def filter(self, record):
        '''Returns True for all records if running in the CLI, else returns
        True.

        When running inside XBMC it calls the xbmc.log() method and prevents
        the message from being double printed to STDOUT.
        '''

        # When running in XBMC, any logged statements will be double printed
        # since we are calling xbmc.log() explicitly. Therefore we return False
        # so every log message is filtered out and not printed again.
        if CLI_MODE:
            return True
        else:
            # Must not be imported until here because of import order issues
            # when running in CLI
            from xbmcswift2 import xbmc
            xbmc_level = XBMCFilter.xbmc_levels.get(
                XBMCFilter.python_to_xbmc.get(record.levelname))
            xbmc.log('%s%s' % (self.prefix, record.getMessage()), xbmc_level)
            return False


if CLI_MODE:
    GLOBAL_LOG_LEVEL = logging.INFO
else:
    GLOBAL_LOG_LEVEL = logging.DEBUG


def setup_log(name):
    '''Returns a logging instance for the provided name. The returned
    object is an instance of logging.Logger. Logged messages will be
    printed to stderr when running in the CLI, or forwarded to XBMC's
    log when running in XBMC mode.
    '''
    _log = logging.getLogger(name)
    _log.setLevel(GLOBAL_LOG_LEVEL)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(name)s] %(message)s')
    handler.setFormatter(formatter)
    _log.addHandler(handler)
    _log.addFilter(XBMCFilter('[%s] ' % name))
    return _log


# The xbmcswift2 log
# Plugin writers should use plugin.log instead.
log = setup_log('xbmcswift2')
