ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

YUICOMPRESSOR_VERSION = 2.4.7
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar

HTMLCOMPRESSOR_VERSION = 1.5.3
HTMLCOMPRESSOR = bin/htmlcompressor-$(HTMLCOMPRESSOR_VERSION).jar


all: $(ALL)

touch:
	touch src/*

clean:
	-rm -r out


out/%.js: src/%.js $(YUICOMPRESSOR)
	@sh bin/compressor.sh "$<" "$@" "$(YUICOMPRESSOR)"

out/%.css: src/%.css $(YUICOMPRESSOR)
	@sh bin/compressor.sh "$<" "$@" "$(YUICOMPRESSOR)"

out/%.html: src/%.html $(HTMLCOMPRESSOR)
	@exec sh bin/compressor.sh $< $@ $(HTMLCOMPRESSOR)

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
