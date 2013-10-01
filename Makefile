NAME = plugin.video.xbmctorrent
VERSION := 0.2.$(shell git rev-list HEAD --count)
ZIP_FILE := $(NAME)_$(VERSION).zip

all: clean version zip

version:
	sed s/\$$VERSION/$(VERSION)/g < addon.xml.tpl > addon.xml

zip:
	git archive --prefix $(NAME)/ master | tar -x -C /tmp
	sed s/\$$VERSION/$(VERSION)/g < addon.xml.tpl > /tmp/$(NAME)/addon.xml
	cp -R resources/bin /tmp/$(NAME)/resources
	cd /tmp && zip -9 -r $(ZIP_FILE) $(NAME)
	mv /tmp/$(ZIP_FILE) .
	rm -rf /tmp/$(NAME)

clean:
	rm -rf addon.xml
	rm -rf /tmp/$(NAME)
