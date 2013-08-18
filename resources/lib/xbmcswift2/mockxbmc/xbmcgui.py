class ListItem(object):
    def __init__(self, label=None, label2=None, iconImage=None, thumbnailImage=None, path=None):
        self.label = label
        self.label2 = label2
        self.iconImage = iconImage
        self.thumbnailImage = thumbnailImage
        self.path = path
        self.properties = {}
        self.stream_info = {}
        self.selected = False
        self.infolabels = {}

    def addContextMenuItems(self, items, replaceItems=False):
        self.context_menu_items = items
    
    def getLabel(self):
        return self.label

    def getLabel2(self):
        return self.label2

    def getProperty(self, key):
        return self.properties[key.lower()]

    def isSelected(self):
        return self.selected

    def select(self, selected):
        self.selected = selected

    def setIconImage(self, icon):
        self.iconImage = icon

    def setInfo(self, type, infoLabels):
        assert type in ['video', 'music', 'pictures']
        self.infolabels.update(infoLabels)

    def setLabel(self, label):
        self.label = label

    def setLabel2(self, label2):
        self.label2 = label2

    def setPath(self, path):
        self.path = path

    def setProperty(self, key, value):
        self.properties[key.lower()] = value

    def addStreamInfo(self, stream_type, stream_values):
        self.stream_info.update({stream_type: stream_values})

    def setThumbnailImage(self, thumb):
        self.thumbnailImage = thumb
        


