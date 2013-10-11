XBMCtorrent
===========

What it is
----------
XBMCtorrent allows you to stream bittorrent magnet links right from XBMC, without having to wait for the whole file to download, thanks to sequential download (see FAQ).

Demo
----
http://www.youtube.com/watch?v=NQiC62ig3N0

[![XBMCtorrent Demo Video](http://img.youtube.com/vi/NQiC62ig3N0/0.jpg)](http://www.youtube.com/watch?v=NQiC62ig3N0)

Supported Platforms
-------------------
* Windows x32 x64
* OS X x64
* Linux x64
* Raspberry Pi (very early)

How it works
------------
XBMCtorrent is actually two parts:
* _XBMCtorrent_: the addon written in Python.
* `torrent2http`: a custom bittorrent client written in Go and leveraging libtorrent-rasterbar, that turns magnet links into HTTP endpoints, using sequential download.

If you feel adventurous, you can find the `torrent2http` and `libtorrent-go` sources at:
* https://github.com/steeve/libtorrent-go
* https://github.com/steeve/torrent2http


Discussions
-----------
Two threads are active, on [XBMC HUB](http://www.xbmchub.com/forums/general-video-addon-discussion/13153-%5Balpha%5D-xbmctorrent-torrent-streaming-xbmc.html) and [XBMC.org](http://forum.xbmc.org/showthread.php?tid=174736).


FAQ
---
#### Does it work with all torrents?
It works with most. Some torrents are known not to work. However, x264 and Xvid ones generally work pretty well, although some won't work yet. Some AVI files don't like to be streamed over HTTP, so YMMV. Of course, the goal is to shrink the number of torrents that don't work.

#### Can I seek in a video?
Issue: [steeve/torrent2http#1](https://github.com/steeve/torrent2http/issues/1)
Not yet. This is scheduled, but currently if you try to seek into a video, it won't work and will stop playback.

#### Can it stream HD?
Of course! 720p and 1080p work fine, provided you have enough bandwidth, and there are enough people on the torrent (see video).

#### Why no Android?
Let's just say: not yet. First of all, I don't have an Android device to test it to. Also, it [seems to be possible](https://github.com/eliasnaur/goandroid), we'll see how the demand evolves on that front.

#### Doesn't sequential download on bittorrent is bad?
Generally, yes. However, XBMCtorrent respects the same [requirements "defined" by uTorrent 3](http://www.utorrent.com/help/faq/ut3#faq2[/url]). Also, XBMCtorrent tries to make it up to the swarm by seeding while you watch the movie.

#### What about seeding?
XBMCtorrent will seed the file you're watching until it's finished playing. For instance, if the download of a 2 hours long movie is finished in 10 minutes, you'll continue seeding it until you finish watching the movie. This is by design, to make up for the fact that we are using sequential download.

#### Does it downloads the whole file? Do I need the space? Is it ever deleted?
Yes and yes. XBMCtorrent will pre-allocate the whole file before download. So if you want to watch a 4GB video, you'll need the 4GB. The file is deleted once you stop watching it.

#### Where is the file located? Can I change it?
Currently the file is download in the same directory as the torrent2http executable (in resources/bin/<OS>/ in the addon directory). You cannot change it yet, but that will be configurable in the near future.

#### Can I keep it after playback?
Not yet, but there will be a flag to enable that.

#### Why are you using Google Analytics? Can I disable it?
First of all, your whole IP isn't tracked. Only the first 3 parts of it, thanks to Analytics [Anonymous Mode](https://developers.google.com/analytics/devguides/collection/gajs/methods/gaJSApi_gat?csw=1#_gat._anonymizeIp). So for instance, if your IP is A.B.C.D, only A.B.C.0 will be logged.
Also, Google Analytics is a great tool to enable real data driven development. I can now concentrate on what really matters.
And finally, of course you can disable it altogether in the addon settings.

#### How can I report a bug?
Please, file an issue :)
