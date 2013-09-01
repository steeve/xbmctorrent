NAME = plugin.video.xbmctorrent
VERSION := 0.1-$(shell git rev-parse --short HEAD)
ZIP_FILE := $(NAME)_$(VERSION).zip

all: version zip

version:
	sed s/\$$VERSION/$(VERSION)/g < addon.xml.tpl > addon.xml

zip:
	git archive --prefix $(NAME)/ master | tar -x -C /tmp
	cp -R resources/bin /tmp/$(NAME)/resources
	cd /tmp && zip -9 -r $(ZIP_FILE) $(NAME)
	mv /tmp/$(ZIP_FILE) .

