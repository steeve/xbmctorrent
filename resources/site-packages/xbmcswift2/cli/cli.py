'''
    xbmcswift2.cli.cli
    ------------------

    The main entry point for the xbmcswift2 console script. CLI commands can be
    registered in this module.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''
import sys
from optparse import OptionParser

from xbmcswift2.cli.app import RunCommand
from xbmcswift2.cli.create import CreateCommand


# TODO: Make an ABC for Command
COMMANDS = {
    RunCommand.command: RunCommand,
    CreateCommand.command: CreateCommand,
}


# TODO: Make this usage dynamic based on COMMANDS dict
USAGE = '''%prog <command>

Commands:
    create
        Create a new plugin project.

    run
        Run an xbmcswift2 plugin from the command line.

Help:
    To see options for a command, run `xbmcswift2 <command> -h`
'''


def main():
    '''The entry point for the console script xbmcswift2.

    The 'xbcmswift2' script is command bassed, so the second argument is always
    the command to execute. Each command has its own parser options and usages.
    If no command is provided or the -h flag is used without any other
    commands, the general help message is shown.
    '''
    parser = OptionParser()
    if len(sys.argv) == 1:
        parser.set_usage(USAGE)
        parser.error('At least one command is required.')

    # spy sys.argv[1] in order to use correct opts/args
    command = sys.argv[1]

    if command == '-h':
        parser.set_usage(USAGE)
        opts, args = parser.parse_args()

    if command not in COMMANDS.keys():
        parser.error('Invalid command')

    # We have a proper command, set the usage and options list according to the
    # specific command
    manager = COMMANDS[command]
    if hasattr(manager, 'option_list'):
        for args, kwargs in manager.option_list:
            parser.add_option(*args, **kwargs)
    if hasattr(manager, 'usage'):
        parser.set_usage(manager.usage)

    opts, args = parser.parse_args()

    # Since we are calling a specific comamnd's manager, we no longer need the
    # actual command in sys.argv so we slice from position 1
    manager.run(opts, args[1:])
