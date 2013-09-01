from xbmcswift import Module

playlist = Module(__name__)

@playlist.route('/add/')
def add_to_playlist():
    items = [playlist.qs_args]
    return playlist._plugin.add_to_playlist(items)
