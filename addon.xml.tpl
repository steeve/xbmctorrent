<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="plugin.video.xbmctorrent" name="XBMCtorrent" version="$VERSION" provider-name="steeve">
    <requires>
        <import addon="xbmc.python"          version="2.1.0"/>
        <import addon="plugin.video.youtube" version="4.4.6"/>
    </requires>
    <extension point="xbmc.python.pluginsource" library="addon.py">
        <provides>video</provides>
    </extension>
    <extension point="xbmc.addon.repository" name="XBMCtorrent Autoupdate Repository">
        <info compressed="true">https://xbmctorrent.herokuapp.com/addons.xml</info>
        <checksum>https://xbmctorrent.herokuapp.com/addons.xml.md5</checksum>
        <datadir zip="true">https://xbmctorrent.herokuapp.com</datadir>
    </extension>
    <extension point="xbmc.addon.metadata">
        <platform>all</platform>
        <website><![CDATA[http://j.mp/xbmctorrent]]></website>
        <forum><![CDATA[http://j.mp/xbmctorrent]]></forum>
        <source><![CDATA[https://github.com/steeve/xbmctorrent]]></source>
        <language></language>
        <license><![CDATA[GNU GENERAL PUBLIC LICENSE. Version 3, 29 June 2007]]></license>
        <summary><![CDATA[XBMCtorrent: Torrent streaming for XBMC.]]></summary>
        <description><![CDATA[XBMCtorrent allows you to stream bittorrent magnet links right from XBMC, without having to wait for the whole file to download, thanks to sequential download.]]></description>
    </extension>
</addon>
