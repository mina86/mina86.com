ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

YUICOMPRESSOR_VERSION = 2.4.7
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar

HTMLCOMPRESSOR_VERSION = 1.5.3
HTMLCOMPRESSOR = bin/htmlcompressor-1.5.3.jar


all: $(ALL)

touch:
	touch src/*

clean:
	-rm -r out



out/%: out/%.with-message
	mv -- $< $@

out/%.with-message: out/%.compiled
	echo -n '/*See github.com/mina86/mina86.com*/' | cat - $< >$@

out/%.js.compiled: src/%.js $(YUICOMPRESSOR)
	@exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type js -o $@ $<

out/%.css.compiled: src/%.css $(YUICOMPRESSOR)
	@exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type css -o $@ $<

out/%.html: src/%.html $(HTMLCOMPRESSOR)
	case "$<" in */[0-9]-*) exec sh bin/xml-filter.sh --add-note $< $@ $(HTMLCOMPRESSOR); esac; \
	exec sh bin/xml-filter.sh $< $@ $(HTMLCOMPRESSOR)

out/html5.js: src/html5.js
	exec cp -- $< $@

bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar: bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip
	unzip -j $< -d $(dir $@) yuicompressor-$(YUICOMPRESSOR_VERSION)/build/yuicompressor-$(YUICOMPRESSOR_VERSION).jar
	touch $@

bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip:
	wget -O $@ https://github.com/downloads/yui/yuicompressor/$(notdir $@)


$(HTMLCOMPRESSOR):
	wget -O $@ http://htmlcompressor.googlecode.com/files/$(notdir $@)


.PHONY: touch clean
.DELETE_ON_ERROR:
.INTERMEDIATE: bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip
