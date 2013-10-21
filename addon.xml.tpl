<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.xbmctorrent" name="XBMCtorrent" version="$VERSION" provider-name="steeve">
    <requires>
        <import addon="xbmc.python" version="2.1.0"/>
        <import addon="script.module.torrent2http" version="0.1.0" />
        <import addon="plugin.video.youtube" version="4.4.6" />
    </requires>
    <extension point="xbmc.python.pluginsource" library="addon.py">
        <provides>video</provides>
    </extension>
    <extension point="xbmc.addon.metadata">
        <platform>all</platform>
        <source>https://github.com/steeve/xbmctorrent</source>
        <language></language>
        <summary>Watch torrents directly from XBMC.</summary>
        <description>Watch torrents directly from XBMC.</description>
    </extension>
</addon>
