import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))
from xbmctorrent import plugin


if __name__ == '__main__':
    plugin.run()
