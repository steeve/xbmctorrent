import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from xbmcswift2 import Plugin
from BeautifulSoup import BeautifulSoup
import requests
from itertools import izip
from contextlib import closing
import xbmc
import xbmcgui
import urllib
import re
import json


plugin = Plugin()


UA = "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11"


def get_url(url):
    import urllib2
    req = urllib2.Request(url)
    req.add_header('User-Agent', UA)
    with closing(urllib2.urlopen(req)) as response:
        return response.read()


def make_http_torrent_url(magnet_uri):
    return "http://localhost:5000/%s" % magnet_uri


@plugin.route("/")
def index():
    return [
        {"label": "EZTV", "path": plugin.url_for("eztv_index"), "is_playable": False},
        {"label": "The Pirate Bay", "path": plugin.url_for("piratebay_search_first"), "is_playable": False},
    ]


@plugin.route("/play/<magnet_uri>")
def play(magnet_uri):
    plugin.set_resolved_url({
        "path": make_http_torrent_url(magnet_uri),
        "is_playable": True,
    })

    state_str = ['Queued', 'Checking', 'Downloading metadata', \
                 'Downloading', 'Finished', 'Seeding', 'Allocating', "Checking resume data"]

    dialog = xbmcgui.DialogProgress()
    dialog.create(plugin.name)
    while not xbmc.Player().isPlayingVideo():
        if dialog.iscanceled():
            xbmc.Player().stop()
            break
        status = json.loads(get_url("http://localhost:5000/status"))
        if status["state"] >= 0:
            dialog.update(
                int(status["progress"] * 100),
                state_str[status["state"]],
                "%.2f%% D:%.2fkb/s U:%.2fkb/s" % (status["progress"] * 100, status["download_rate"], status["upload_rate"]),
                "S:%d P:%d" % (status["num_seeds"], status["num_peers"])
            )
        xbmc.sleep(100)
    dialog.close()



@plugin.route("/tpb", name="piratebay_search_first")
@plugin.route("/tpb/<query>/<page>")
def piratebay_search(query=None, page=0):
    page = int(page)
    if not query:
        kb = xbmc.Keyboard("", "Search")
        kb.doModal()
        if kb.isConfirmed():
            query = kb.getText()
    if query:
        query_url = "http://thepiratebay.sx/search/%s/%d/7/0" % (urllib.quote(query), page)
        soup = BeautifulSoup(get_url(query_url))
        nodes = soup.findAll("div", "detName")

        next_page = {
            "label": "Next page...",
            "path": plugin.url_for("piratebay_search", query=query, page=page + 1),
            "is_playable": False,
        }
        yield next_page
        for node in nodes:
            seeds, peers = map(lambda x: x.text, node.parent.parent.findAll("td")[2:])
            magnet_node = node.parent.findAll("a")[1]
            desc_node = node.parent.findAll("font", "detDesc")[0]
            size = re.search("Size (.*?),", desc_node.text).group(1)
            text = "%s (%s S:%s P:%s)" % (node.a.text, size.replace("&nbsp;", " "), seeds, peers)
            yield {
                "label": text,
                "path": plugin.url_for("play", magnet_uri=magnet_node["href"]),
                "is_playable": True,
            }
        yield next_page


@plugin.route("/eztv")
def eztv_index():
    response = requests.get("https://eztv.it/showlist/")
    soup = BeautifulSoup(response.text)
    nodes = soup.findAll("a", "thread_link")

    for node in nodes:
        show_id, show_name = node["href"].split("/")[2:4]
        yield {
            "label": node.text,
            "path": plugin.url_for("eztv_get_show", show_id=show_id, show_name=show_name),
            "thumbnail": "http://ezimg.it/t/%s/main.png" % show_name.replace("-", "_"),
            "is_playable": False,
        }

@plugin.route("/eztv/shows/<show_id>/<show_name>")
def eztv_get_show(show_id, show_name):
    response = requests.get("https://eztv.it/shows/%s/%s" % (show_id, show_name))
    soup = BeautifulSoup(response.text)
    for node_text, node_magnet in izip(soup.findAll("a", "epinfo"), soup.findAll("a", "magnet")):
        xbmc.log(node_magnet["href"])
        stream_info = {}
        if "x264" in node_text.text:
            stream_info["codec"] = "h264"
        if "720p" in node_text.text:
            stream_info["width"] = 1280
            stream_info["height"] = 720
        if "1080p" in node_text.text:
            stream_info["width"] = 1920
            stream_info["height"] = 1080
        yield {
            "label": node_text.text,
            "path": plugin.url_for("play", magnet_uri=node_magnet["href"]),
            "is_playable": True,
            "stream_info": stream_info,
        }


if __name__ == '__main__':
    plugin.run()
