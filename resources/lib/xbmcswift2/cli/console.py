'''
    xbmcswift2.cli.console
    ----------------------

    This module contains code to handle CLI interaction.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
'''


def get_max_len(items):
    '''Returns the max of the lengths for the provided items'''
    try:
        return max(len(item) for item in items)
    except ValueError:
        return 0


def display_listitems(items, url):
    '''Displays a list of items along with the index to enable a user
    to select an item.
    '''
    if (len(items) == 2 and items[0].get_label() == '..'
        and items[1].get_played()):
        display_video(items)
    else:
        label_width = get_max_len(item.get_label() for item in items)
        num_width = len(str(len(items)))
        output = []
        for i, item in enumerate(items):
            output.append('[%s] %s (%s)' % (
                str(i).rjust(num_width),
                item.get_label().ljust(label_width),
                item.get_path()))

        line_width = get_max_len(output)
        output.append('-' * line_width)

        header = [
            '',
            '=' * line_width,
            'Current URL: %s' % url,
            '-' * line_width,
            '%s %s Path' % ('#'.center(num_width + 2),
                            'Label'.ljust(label_width)),
            '-' * line_width,
        ]
        print '\n'.join(header + output)


def display_video(items):
    '''Prints a message for a playing video and displays the parent
    listitem.
    '''
    parent_item, played_item = items

    title_line = 'Playing Media %s (%s)' % (played_item.get_label(),
                                            played_item.get_path())
    parent_line = '[0] %s (%s)' % (parent_item.get_label(),
                                   parent_item.get_path())
    line_width = get_max_len([title_line, parent_line])

    output = [
        '-' * line_width,
        title_line,
        '-' * line_width,
        parent_line,
    ]
    print '\n'.join(output)


def get_user_choice(items):
    '''Returns the selected item from provided items or None if 'q' was
    entered for quit.
    '''
    choice = raw_input('Choose an item or "q" to quit: ')
    while choice != 'q':
        try:
            item = items[int(choice)]
            print  # Blank line for readability between interactive views
            return item
        except ValueError:
            # Passed something that cound't be converted with int()
            choice = raw_input('You entered a non-integer. Choice must be an'
                               ' integer or "q": ')
        except IndexError:
            # Passed an integer that was out of range of the list of urls
            choice = raw_input('You entered an invalid integer. Choice must be'
                               ' from above url list or "q": ')
    return None


def continue_or_quit():
    '''Prints an exit message and returns False if the user wants to
    quit.
    '''
    return raw_input('Enter to continue or "q" to quit') != 'q'
