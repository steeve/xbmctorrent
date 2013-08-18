'''
    xbmcswift2.listitem
    ------------------

    This module contains the ListItem class, which acts as a wrapper
    for xbmcgui.ListItem.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
from xbmcswift2 import xbmcgui


class ListItem(object):
    '''A wrapper for the xbmcgui.ListItem class. The class keeps track
    of any set properties that xbmcgui doesn't expose getters for.
    '''
    def __init__(self, label=None, label2=None, icon=None, thumbnail=None,
                 path=None):
        '''Defaults are an emtpy string since xbmcgui.ListItem will not
        accept None.
        '''
        kwargs = {
            'label': label,
            'label2': label2,
            'iconImage': icon,
            'thumbnailImage': thumbnail,
            'path': path,
        }
        #kwargs = dict((key, val) for key, val in locals().items() if val is
        #not None and key != 'self')
        kwargs = dict((key, val) for key, val in kwargs.items()
                      if val is not None)
        self._listitem = xbmcgui.ListItem(**kwargs)

        # xbmc doesn't make getters available for these properties so we'll
        # keep track on our own
        self._icon = icon
        self._path = path
        self._thumbnail = thumbnail
        self._context_menu_items = []
        self.is_folder = True
        self._played = False

    def __repr__(self):
        return ("<ListItem '%s'>" % self.label).encode('utf-8')

    def __str__(self):
        return ('%s (%s)' % (self.label, self.path)).encode('utf-8')

    def get_context_menu_items(self):
        '''Returns the list of currently set context_menu items.'''
        return self._context_menu_items

    def add_context_menu_items(self, items, replace_items=False):
        '''Adds context menu items. If replace_items is True all
        previous context menu items will be removed.
        '''
        for label, action in items:
            assert isinstance(label, basestring)
            assert isinstance(action, basestring)
        if replace_items:
            self._context_menu_items = []
        self._context_menu_items.extend(items)
        self._listitem.addContextMenuItems(items, replace_items)

    def get_label(self):
        '''Sets the listitem's label'''
        return self._listitem.getLabel()

    def set_label(self, label):
        '''Returns the listitem's label'''
        return self._listitem.setLabel(label)

    label = property(get_label, set_label)

    def get_label2(self):
        '''Returns the listitem's label2'''
        return self._listitem.getLabel2()

    def set_label2(self, label):
        '''Sets the listitem's label2'''
        return self._listitem.setLabel2(label)

    label2 = property(get_label2, set_label2)

    def is_selected(self):
        '''Returns True if the listitem is selected.'''
        return self._listitem.isSelected()

    def select(self, selected_status=True):
        '''Sets the listitems selected status to the provided value.
        Defaults to True.
        '''
        return self._listitem.select(selected_status)

    selected = property(is_selected, select)

    def set_info(self, type, info_labels):
        '''Sets the listitems info'''
        return self._listitem.setInfo(type, info_labels)

    def get_property(self, key):
        '''Returns the property associated with the given key'''
        return self._listitem.getProperty(key)

    def set_property(self, key, value):
        '''Sets a property for the given key and value'''
        return self._listitem.setProperty(key, value)

    def add_stream_info(self, stream_type, stream_values):
        '''Adds stream details'''
        return self._listitem.addStreamInfo(stream_type, stream_values)

    def get_icon(self):
        '''Returns the listitem's icon image'''
        return self._icon

    def set_icon(self, icon):
        '''Sets the listitem's icon image'''
        self._icon = icon
        return self._listitem.setIconImage(icon)

    icon = property(get_icon, set_icon)

    def get_thumbnail(self):
        '''Returns the listitem's thumbnail image'''
        return self._thumbnail

    def set_thumbnail(self, thumbnail):
        '''Sets the listitem's thumbnail image'''
        self._thumbnail = thumbnail
        return self._listitem.setThumbnailImage(thumbnail)

    thumbnail = property(get_thumbnail, set_thumbnail)

    def get_path(self):
        '''Returns the listitem's path'''
        return self._path

    def set_path(self, path):
        '''Sets the listitem's path'''
        self._path = path
        return self._listitem.setPath(path)

    path = property(get_path, set_path)

    def get_is_playable(self):
        '''Returns True if the listitem is playable, False if it is a
        directory
        '''
        return not self.is_folder

    def set_is_playable(self, is_playable):
        '''Sets the listitem's playable flag'''
        value = 'false'
        if is_playable:
            value = 'true'
        self.set_property('isPlayable', value)
        self.is_folder = not is_playable

    playable = property(get_is_playable, set_is_playable)

    def set_played(self, was_played):
        '''Sets the played status of the listitem. Used to
        differentiate between a resolved video versus a playable item.
        Has no effect on XBMC, it is strictly used for xbmcswift2.
        '''
        self._played = was_played

    def get_played(self):
        '''Returns True if the video was played.'''
        return self._played

    def as_tuple(self):
        '''Returns a tuple of list item properties:
            (path, the wrapped xbmcgui.ListItem, is_folder)
        '''
        return self.path, self._listitem, self.is_folder

    def as_xbmc_listitem(self):
        '''Returns the wrapped xbmcgui.ListItem'''
        return self._listitem

    @classmethod
    def from_dict(cls, label=None, label2=None, icon=None, thumbnail=None,
                  path=None, selected=None, info=None, properties=None,
                  context_menu=None, replace_context_menu=False,
                  is_playable=None, info_type='video', stream_info=None):
        '''A ListItem constructor for setting a lot of properties not
        available in the regular __init__ method. Useful to collect all
        the properties in a dict and then use the **dct to call this
        method.
        '''
        listitem = cls(label, label2, icon, thumbnail, path)

        if selected is not None:
            listitem.select(selected)

        if info:
            listitem.set_info(info_type, info)

        if is_playable:
            listitem.set_is_playable(True)

        if properties:
            # Need to support existing tuples, but prefer to have a dict for
            # properties.
            if hasattr(properties, 'items'):
                properties = properties.items()
            for key, val in properties:
                listitem.set_property(key, val)

        if stream_info:
            for stream_type, stream_values in stream_info.items():
                listitem.add_stream_info(stream_type, stream_values)

        if context_menu:
            listitem.add_context_menu_items(context_menu, replace_context_menu)

        return listitem
