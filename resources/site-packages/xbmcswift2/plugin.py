'''
    xbmcswift2.plugin
    -----------------

    This module contains the Plugin class. This class handles all of the url
    routing and interaction with XBMC for a plugin.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
import os
import sys
import pickle
import xbmcswift2
from urllib import urlencode
from functools import wraps
from optparse import OptionParser
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

from listitem import ListItem
from logger import log, setup_log
from common import enum
from common import clean_dict
from urls import UrlRule, NotFoundException, AmbiguousUrlException
from xbmcswift2 import (xbmc, xbmcgui, xbmcplugin, xbmcaddon, Request,)

from xbmcmixin import XBMCMixin
from common import Modes, DEBUG_MODES


class Plugin(XBMCMixin):
    '''The Plugin objects encapsulates all the properties and methods necessary
    for running an XBMC plugin. The plugin instance is a central place for
    registering view functions and keeping track of plugin state.

    Usually the plugin instance is created in the main addon.py file for the
    plugin. Typical creation looks like this::

        from xbmcswift2 import Plugin
        plugin = Plugin('Hello XBMC')


    .. versionchanged:: 0.2
        The *addon_id* and *filepath* parameters are now optional. They will
        now default to the correct values.

    :param name: The name of the plugin, e.g. 'Academic Earth'.

    :param addon_id: The XBMC addon ID for the plugin, e.g.
                     'plugin.video.academicearth'. This parameter is now
                     optional and is really only useful for testing purposes.
                     If it is not provided, the correct value will be parsed
                     from the addon.xml file.

    :param filepath: Optional parameter. If provided, it should be the path to
                     the addon.py file in the root of the addon directoy. This
                     only has an effect when xbmcswift2 is running on the
                     command line. Will default to the current working
                     directory since xbmcswift2 requires execution in the root
                     addon directoy anyway. The parameter still exists to ease
                     testing.
    '''

    def __init__(self, name=None, addon_id=None, filepath=None, info_type=None):
        self._name = name
        self._routes = []
        self._view_functions = {}

        # addon_id is no longer required as it can be parsed from addon.xml
        if addon_id:
            self._addon = xbmcaddon.Addon(id=addon_id)
        else:
            self._addon = xbmcaddon.Addon()

        self._addon_id = addon_id or self._addon.getAddonInfo('id')
        self._name = name or self._addon.getAddonInfo('name')

        self._info_type = info_type
        if not self._info_type:
            types = {
                'video': 'video',
                'audio': 'music',
                'image': 'pictures',
            }
            self._info_type = types.get(self._addon_id.split('.')[1], 'video')

        # Keeps track of the added list items
        self._current_items = []

        # Gets initialized when self.run() is called
        self._request = None

        # A flag to keep track of a call to xbmcplugin.endOfDirectory()
        self._end_of_directory = False

        # Keep track of the update_listing flag passed to
        # xbmcplugin.endOfDirectory()
        self._update_listing = False

        # The plugin's named logger
        self._log = setup_log(self._addon_id)

        # The path to the storage directory for the addon
        self._storage_path = xbmc.translatePath(
            'special://profile/addon_data/%s/.storage/' % self._addon_id)
        if not os.path.isdir(self._storage_path):
            os.makedirs(self._storage_path)

        # If we are runing in CLI, we need to load the strings.xml manually
        # Since xbmcswift2 currently relies on execution from an addon's root
        # directly, we can rely on cwd for now...
        if xbmcswift2.CLI_MODE:
            from xbmcswift2.mockxbmc import utils
            if filepath:
                addon_dir = os.path.dirname(filepath)
            else:
                addon_dir = os.getcwd()
            strings_fn = os.path.join(addon_dir, 'resources', 'language',
                                      'English', 'strings.xml')
            utils.load_addon_strings(self._addon, strings_fn)

    @property
    def info_type(self):
        return self._info_type

    @property
    def log(self):
        '''The log instance for the plugin. Returns an instance of the
        stdlib's ``logging.Logger``. This log will print to STDOUT when running
        in CLI mode and will forward messages to XBMC's log when running in
        XBMC. Some examples::

            plugin.log.debug('Debug message')
            plugin.log.warning('Warning message')
            plugin.log.error('Error message')
        '''
        return self._log

    @property
    def id(self):
        '''The id for the addon instance.'''
        return self._addon_id

    @property
    def storage_path(self):
        '''A full path to the storage folder for this plugin's addon data.'''
        return self._storage_path

    @property
    def addon(self):
        '''This plugin's wrapped instance of xbmcaddon.Addon.'''
        return self._addon

    @property
    def added_items(self):
        '''The list of currently added items.

        Even after repeated calls to :meth:`~xbmcswift2.Plugin.add_items`, this
        property will contain the complete list of added items.
        '''
        return self._current_items

    def clear_added_items(self):
        # TODO: This shouldn't be exposed probably...
        self._current_items = []

    @property
    def handle(self):
        '''The current plugin's handle. Equal to ``plugin.request.handle``.'''
        return self.request.handle

    @property
    def request(self):
        '''The current :class:`~xbmcswift2.Request`.

        Raises an Exception if the request hasn't been initialized yet via
        :meth:`~xbmcswift2.Plugin.run()`.
        '''
        if self._request is None:
            raise Exception('It seems the current request has not been '
                            'initialized yet. Please ensure that '
                            '`plugin.run()` has been called before attempting '
                            'to access the current request.')
        return self._request

    @property
    def name(self):
        '''The addon's name'''
        return self._name

    def _parse_request(self, url=None, handle=None):
        '''Handles setup of the plugin state, including request
        arguments, handle, mode.

        This method never needs to be called directly. For testing, see
        plugin.test()
        '''
        # To accomdate self.redirect, we need to be able to parse a full url as
        # well
        if url is None:
            url = sys.argv[0]
            if len(sys.argv) == 3:
                url += sys.argv[2]
        if handle is None:
            handle = sys.argv[1]
        return Request(url, handle)

    def register_module(self, module, url_prefix):
        '''Registers a module with a plugin. Requires a url_prefix that
        will then enable calls to url_for.

        :param module: Should be an instance `xbmcswift2.Module`.
        :param url_prefix: A url prefix to use for all module urls,
                           e.g. '/mymodule'
        '''
        module._plugin = self
        module._url_prefix = url_prefix
        for func in module._register_funcs:
            func(self, url_prefix)

    def cached_route(self, url_rule, name=None, options=None, TTL=None):
        '''A decorator to add a route to a view and also apply caching. The
        url_rule, name and options arguments are the same arguments for the
        route function. The TTL argument if given will passed along to the
        caching decorator.
        '''
        route_decorator = self.route(url_rule, name=name, options=options)
        if TTL:
            cache_decorator = self.cached(TTL)
        else:
            cache_decorator = self.cached()

        def new_decorator(func):
            return route_decorator(cache_decorator(func))
        return new_decorator

    def route(self, url_rule, name=None, options=None):
        '''A decorator to add a route to a view. name is used to
        differentiate when there are multiple routes for a given view.'''
        # TODO: change options kwarg to defaults
        def decorator(f):
            view_name = name or f.__name__
            self.add_url_rule(url_rule, f, name=view_name, options=options)
            return f
        return decorator

    def add_url_rule(self, url_rule, view_func, name, options=None):
        '''This method adds a URL rule for routing purposes. The
        provided name can be different from the view function name if
        desired. The provided name is what is used in url_for to build
        a URL.

        The route decorator provides the same functionality.
        '''
        rule = UrlRule(url_rule, view_func, name, options)
        if name in self._view_functions.keys():
            # TODO: Raise exception for ambiguous views during registration
            log.warning('Cannot add url rule "%s" with name "%s". There is '
                        'already a view with that name', url_rule, name)
            self._view_functions[name] = None
        else:
            log.debug('Adding url rule "%s" named "%s" pointing to function '
                      '"%s"', url_rule, name, view_func.__name__)
            self._view_functions[name] = rule
        self._routes.append(rule)

    def url_for(self, endpoint, **items):
        '''Returns a valid XBMC plugin URL for the given endpoint name.
        endpoint can be the literal name of a function, or it can
        correspond to the name keyword arguments passed to the route
        decorator.

        Raises AmbiguousUrlException if there is more than one possible
        view for the given endpoint name.
        '''
        try:
            rule = self._view_functions[endpoint]
        except KeyError:
            try:
                rule = (rule for rule in self._view_functions.values() if rule.view_func == endpoint).next()
            except StopIteration:
                raise NotFoundException(
                    '%s doesn\'t match any known patterns.' % endpoint)

        # rule can be None since values of None are allowed in the
        # _view_functions dict. This signifies more than one view function is
        # tied to the same name.
        if not rule:
            # TODO: Make this a regular exception
            raise AmbiguousUrlException

        pathqs = rule.make_path_qs(items)
        return 'plugin://%s%s' % (self._addon_id, pathqs)

    def _dispatch(self, path):
        for rule in self._routes:
            try:
                view_func, items = rule.match(path)
            except NotFoundException:
                continue
            log.info('Request for "%s" matches rule for function "%s"',
                     path, view_func.__name__)
            listitems = view_func(**items)

            # Only call self.finish() for UI container listing calls to plugin
            # (handle will be >= 0). Do not call self.finish() when called via
            # RunPlugin() (handle will be -1).
            if not self._end_of_directory and self.handle >= 0:
                if listitems is None:
                    self.finish(succeeded=False)
                else:
                    listitems = self.finish(listitems)

            return listitems
        raise NotFoundException, 'No matching view found for %s' % path

    def redirect(self, url):
        '''Used when you need to redirect to another view, and you only
        have the final plugin:// url.'''
        # TODO: Should we be overriding self.request with the new request?
        new_request = self._parse_request(url=url, handle=self.request.handle)
        log.debug('Redirecting %s to %s', self.request.path, new_request.path)
        return self._dispatch(new_request.path)

    def run(self, test=False):
        '''The main entry point for a plugin.'''
        self._request = self._parse_request()
        log.debug('Handling incoming request for %s', self.request.path)
        items = self._dispatch(self.request.path)

        # Close any open storages which will persist them to disk
        if hasattr(self, '_unsynced_storages'):
            for storage in self._unsynced_storages.values():
                log.debug('Saving a %s storage to disk at "%s"',
                          storage.file_format, storage.filename)
                storage.close()

        return items
