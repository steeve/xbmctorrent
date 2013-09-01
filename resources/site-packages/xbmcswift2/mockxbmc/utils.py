from xml.dom.minidom import parse


def load_addon_strings(addon, filename):
    '''This is not an official XBMC method, it is here to faciliate
    mocking up the other methods when running outside of XBMC.'''
    def get_strings(fn):
        xml = parse(fn)
        strings = dict((tag.getAttribute('id'), tag.firstChild.data) for tag in xml.getElementsByTagName('string'))
        #strings = {}
        #for tag in xml.getElementsByTagName('string'):
            #strings[tag.getAttribute('id')] = tag.firstChild.data
        return strings
    addon._strings = get_strings(filename)


def get_addon_id(addonxml):
    '''Parses an addon id from the given addon.xml filename.'''
    xml = parse(addonxml)
    addon_node = xml.getElementsByTagName('addon')[0]
    return addon_node.getAttribute('id')


def get_addon_name(addonxml):
    '''Parses an addon name from the given addon.xml filename.'''
    xml = parse(addonxml)
    addon_node = xml.getElementsByTagName('addon')[0]
    return addon_node.getAttribute('name')
