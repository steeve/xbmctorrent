'''
    xbmcswift2.cli
    ----------------

    This package contains modules that are used only when running xbmcswift2 in
    CLI mode. Nothing from this package should be called from addon code.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''


def Option(*args, **kwargs):
    '''Returns a tuple of args, kwargs passed to the function. Useful for
    recording arguments for future function calls.
    '''
    return args, kwargs
