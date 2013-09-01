from xbmcswift2 import Plugin


plugin = Plugin()


@plugin.route('/')
def index():
    item = {
        'label': 'Hello XBMC!',
        'path': 'http://s3.amazonaws.com/KA-youtube-converted/JwO_25S_eWE.mp4/JwO_25S_eWE.mp4',
        'is_playable': True
    }
    return [item]


if __name__ == '__main__':
    plugin.run()
