from xbmctorrent import plugin, magnet, scrapers
from xbmctorrent.ga import tracked
from xbmctorrent.utils import ensure_fanart
from xbmctorrent.platform import PLATFORM
from xbmctorrent.scrapers import \
    MODULES, \
    eztv, \
    yify, \
    kickass, \
    tpb, \
    btdigg, \
    bitsnoop, \
    extratorrent, \
    nyaa


@plugin.route("/")
@ensure_fanart
@tracked(force=True)
def index():
    if PLATFORM["os"] not in ["android", "linux", "windows", "darwin"]:
        plugin.notify("Your system \"%(os)s_%(arch)s\" is not supported." % PLATFORM, delay=15000)

    for module in MODULES:
        yield {
            "label": module["name"],
            "thumbnail": module["image"],
            "path": plugin.url_for(module["view"]),
        }
