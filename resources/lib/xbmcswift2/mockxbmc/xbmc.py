import tempfile
import os, errno
from xbmcswift2 import log
from xbmcswift2.cli.create import get_value


TEMP_DIR = os.path.join(tempfile.gettempdir(), 'xbmcswift2_debug')
log.info('Using temp directory %s', TEMP_DIR)


def _create_dir(path):
    '''Creates necessary directories for the given path or does nothing
    if the directories already exist.
    '''
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def log(msg, level=0):
    levels = [
        'LOGDEBUG',
        'LOGINFO',
        'LOGNOTICE',
        'LOGWARNING',
        'LOGERROR',
        'LOGSEVERE',
        'LOGFATAL',
        'LOGNONE',
    ]
    #print '%s - %s' % (levels[level], msg)

def translatePath(path):
    '''Creates folders in the OS's temp directory. Doesn't touch any
    possible XBMC installation on the machine. Attempting to do as
    little work as possible to enable this function to work seamlessly.
    '''
    valid_dirs = ['xbmc', 'home', 'temp', 'masterprofile', 'profile',
        'subtitles', 'userdata', 'database', 'thumbnails', 'recordings',
        'screenshots', 'musicplaylists', 'videoplaylists', 'cdrips', 'skin',
    ]

    assert path.startswith('special://'), 'Not a valid special:// path.'
    parts = path.split('/')[2:]
    assert len(parts) > 1, 'Need at least a single root directory'
    assert parts[0] in valid_dirs, '%s is not a valid root dir.' % parts[0]

    # We don't want to swallow any potential IOErrors here, so only makedir for
    # the root dir, the user is responsible for making any further child dirs
    _create_dir(os.path.join(TEMP_DIR, parts[0]))

    return os.path.join(TEMP_DIR, *parts)

class Keyboard(object):
    def __init__(self, default='', heading='', hidden=False):
        self._heading = heading
        self._default = default
        self._hidden = hidden
        self._confirmed = False
        self._input = None
        
    def setDefault(self, default):
        self._default = default

    def setHeading(self, heading):
        self._heading = heading

    def setHiddenInput(self, hidden):
        self._hidden = hidden

    def doModal(self):
        self._confirmed = False
        try:
            self._input = get_value(self._heading, self._default, hidden=self._hidden)
            self._confirmed = True
        except (KeyboardInterrupt, EOFError):
            pass

    def isConfirmed(self):
        return self._confirmed

    def getText(self):
        return self._input
