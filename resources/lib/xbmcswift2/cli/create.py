'''
    xbmcswift2.cli.create
    ---------------------

    This module contains the code to initialize a new XBMC addon project.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
import os
import string
import readline
from os import getcwd
from xml.sax import saxutils
from optparse import OptionParser
from shutil import copytree, ignore_patterns
from getpass import getpass


class CreateCommand(object):
    '''A CLI command to initialize a new XBMC addon project.'''

    command = 'create'
    usage = '%prog create'

    @staticmethod
    def run(opts, args):
        '''Required run function for the 'create' CLI command.'''
        create_new_project()


# Path to skeleton file templates dir
SKEL = os.path.join(os.path.dirname(__file__), 'data')


def error_msg(msg):
    '''A decorator that sets the error_message attribute of the decorated
    function to the provided value.
    '''
    def decorator(func):
        '''Sets the error_message attribute on the provided function'''
        func.error_message = msg
        return func
    return decorator


def parse_cli():
    '''Currently only one positional arg, create.'''
    parser = OptionParser()
    return parser.parse_args()


@error_msg('** Value must be non-blank.')
def validate_nonblank(value):
    '''A callable that retunrs the value passed'''
    return value


@error_msg('** Value must contain only letters or underscores.')
def validate_pluginid(value):
    '''Returns True if the provided value is a valid pluglin id'''
    valid = string.ascii_letters + string.digits + '.'
    return all(c in valid for c in value)


@error_msg('** The provided path must be an existing folder.')
def validate_isfolder(value):
    '''Returns true if the provided path is an existing directory'''
    return os.path.isdir(value)


def get_valid_value(prompt, validator, default=None):
    '''Displays the provided prompt and gets input from the user. This behavior
    loops indefinitely until the provided validator returns True for the user
    input. If a default value is provided, it will be used only if the user
    hits Enter and does not provide a value.

    If the validator callable has an error_message attribute, it will be
    displayed for an invalid value, otherwise a generic message is used.
    '''
    ans = get_value(prompt, default)
    while not validator(ans):
        try:
            print validator.error_message
        except AttributeError:
            print 'Invalid value.'
        ans = get_value(prompt, default)

    return ans


def get_value(prompt, default=None, hidden=False):
    '''Displays the provided prompt and returns the input from the user. If the
    user hits Enter and there is a default value provided, the default is
    returned.
    '''
    _prompt = '%s : ' % prompt
    if default:
        _prompt = '%s [%s]: ' % (prompt, default)

    if hidden:
        ans = getpass(_prompt)
    else:
        ans = raw_input(_prompt)

    # If user hit Enter and there is a default value
    if not ans and default:
        ans = default
    return ans


def update_file(filename, items):
    '''Edits the given file in place, replacing any instances of {key} with the
    appropriate value from the provided items dict. If the given filename ends
    with ".xml" values will be quoted and escaped for XML.
    '''
    # TODO: Implement something in the templates to denote whether the value
    # being replaced is an XML attribute or a value. Perhaps move to dyanmic
    # XML tree building rather than string replacement.
    should_escape = filename.endswith('addon.xml')

    with open(filename, 'r') as inp:
        text = inp.read()

    for key, val in items.items():
        if should_escape:
            val = saxutils.quoteattr(val)
        text = text.replace('{%s}' % key, val)
    output = text

    with open(filename, 'w') as out:
        out.write(output)


def create_new_project():
    '''Creates a new XBMC Addon directory based on user input'''
    readline.parse_and_bind('tab: complete')

    print \
'''
    xbmcswift2 - A micro-framework for creating XBMC plugins.
    xbmc@jonathanbeluch.com
    --
'''
    print 'I\'m going to ask you a few questions to get this project' \
        ' started.'

    opts = {}

    # Plugin Name
    opts['plugin_name'] = get_valid_value(
        'What is your plugin name?',
        validate_nonblank
    )

    # Plugin ID
    opts['plugin_id'] = get_valid_value(
        'Enter your plugin id.',
        validate_pluginid,
        'plugin.video.%s' % (opts['plugin_name'].lower().replace(' ', ''))
    )

    # Parent Directory
    opts['parent_dir'] = get_valid_value(
        'Enter parent folder (where to create project)',
        validate_isfolder,
        getcwd()
    )
    opts['plugin_dir'] = os.path.join(opts['parent_dir'], opts['plugin_id'])
    assert not os.path.isdir(opts['plugin_dir']), \
        'A folder named %s already exists in %s.' % (opts['plugin_id'],
                                                     opts['parent_dir'])

    # Provider
    opts['provider_name'] = get_valid_value(
        'Enter provider name',
        validate_nonblank,
    )

    # Create the project folder by copying over skel
    copytree(SKEL, opts['plugin_dir'], ignore=ignore_patterns('*.pyc'))

    # Walk through all the new files and fill in with out options
    for root, dirs, files in os.walk(opts['plugin_dir']):
        for filename in files:
            update_file(os.path.join(root, filename), opts)

    print 'Projects successfully created in %s.' % opts['plugin_dir']
    print 'Done.'
