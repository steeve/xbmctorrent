'''
    xbmcswift2.urls
    ---------------

    This module contains URLRule class for dealing with url patterns.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
import re
from urllib import urlencode, unquote_plus, quote_plus
from xbmcswift2.common import pickle_dict, unpickle_dict


# TODO: Use regular Exceptions
class AmbiguousUrlException(Exception):
    pass


class NotFoundException(Exception):
    pass


class UrlRule(object):
    '''This object stores the various properties related to a routing URL rule.
    It also provides a few methods to create URLs from the rule or to match a
    given URL against a rule.

    :param url_rule: The relative url pattern for the rule. It may include
                     <var_name> to denote where dynamic variables should be
                     matched.
    :param view_func: The function that should be bound to this rule. This
                      should be an actual function object.

                      .. warning:: The function signature should match any
                                   variable names in the provided url_rule.
    :param name: The name of the url rule. This is used in the reverse process
                 of creating urls for a given rule.
    :param options: A dict containing any default values for the url rule.
    '''

    def __init__(self, url_rule, view_func, name, options):
        self._name = name
        self._url_rule = url_rule
        self._view_func = view_func
        self._options = options or {}
        self._keywords = re.findall(r'\<(.+?)\>', url_rule)

        #change <> to {} for use with str.format()
        self._url_format = self._url_rule.replace('<', '{').replace('>', '}')

        # Make a regex pattern for matching incoming URLs
        rule = self._url_rule
        if rule != '/':
            # Except for a path of '/', the trailing slash is optional.
            rule = self._url_rule.rstrip('/') + '/?'
        p = rule.replace('<', '(?P<').replace('>', '>[^/]+?)')

        try:
            self._regex = re.compile('^' + p + '$')
        except re.error, e:
            raise ValueError, ('There was a problem creating this URL rule. '
                               'Ensure you do not have any unpaired angle '
                               'brackets: "<" or ">"')

    def __eq__(self, other):
        return (
            (self._name, self._url_rule, self._view_func, self._options) ==
            (other._name, other._url_rule, other._view_func, other._options)
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    def match(self, path):
        '''Attempts to match a url to the given path. If successful, a tuple is
        returned. The first item is the matchd function and the second item is
        a dictionary containing items to be passed to the function parsed from
        the provided path.

        If the provided path does not match this url rule then a
        NotFoundException is raised.
        '''
        m = self._regex.search(path)
        if not m:
            raise NotFoundException

        # urlunencode the values
        items = dict((key, unquote_plus(val))
                     for key, val in m.groupdict().items())

        # unpickle any items if present
        items = unpickle_dict(items)

        # We need to update our dictionary with default values provided in
        # options if the keys don't already exist.
        [items.setdefault(key, val) for key, val in self._options.items()]
        return self._view_func, items

    def _make_path(self, items):
        '''Returns a relative path for the given dictionary of items.

        Uses this url rule's url pattern and replaces instances of <var_name>
        with the appropriate value from the items dict.
        '''
        for key, val in items.items():
            if not isinstance(val, basestring):
                raise TypeError, ('Value "%s" for key "%s" must be an instance'
                                  ' of basestring' % (val, key))
            items[key] = quote_plus(val)

        try:
            path = self._url_format.format(**items)
        except AttributeError:
            # Old version of python
            path = self._url_format
            for key, val in items.items():
                path = path.replace('{%s}' % key, val)
        return path

    def _make_qs(self, items):
        '''Returns a query string for the given dictionary of items. All keys
        and values in the provided items will be urlencoded. If necessary, any
        python objects will be pickled before being urlencoded.
        '''
        return urlencode(pickle_dict(items))

    def make_path_qs(self, items):
        '''Returns a relative path complete with query string for the given
        dictionary of items.

        Any items with keys matching this rule's url pattern will be inserted
        into the path. Any remaining items will be appended as query string
        parameters.

        All items will be urlencoded. Any items which are not instances of
        basestring, or int/long will be pickled before being urlencoded.

        .. warning:: The pickling of items only works for key/value pairs which
                     will be in the query string. This behavior should only be
                     used for the simplest of python objects. It causes the
                     URL to get very lengthy (and unreadable) and XBMC has a
                     hard limit on URL length. See the caching section if you
                     need to persist a large amount of data between requests.
        '''
        # Convert any ints and longs to strings
        for key, val in items.items():
            if isinstance(val, (int, long)):
                items[key] = str(val)

        # First use our defaults passed when registering the rule
        url_items = dict((key, val) for key, val in self._options.items()
                         if key in self._keywords)

        # Now update with any items explicitly passed to url_for
        url_items.update((key, val) for key, val in items.items()
                         if key in self._keywords)

        # Create the path
        path = self._make_path(url_items)

        # Extra arguments get tacked on to the query string
        qs_items = dict((key, val) for key, val in items.items()
                        if key not in self._keywords)
        qs = self._make_qs(qs_items)

        if qs:
            return '?'.join([path, qs])
        return path

    @property
    def regex(self):
        '''The regex for matching paths against this url rule.'''
        return self._regex

    @property
    def view_func(self):
        '''The bound function'''
        return self._view_func

    @property
    def url_format(self):
        '''The url pattern'''
        return self._url_format

    @property
    def name(self):
        '''The name of this url rule.'''
        return self._name

    @property
    def keywords(self):
        '''The list of path keywords for this url rule.'''
        return self._keywords
