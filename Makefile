ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

YUICOMPRESSOR_VERSION = 2.4.8
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


$(YUICOMPRESSOR):
	wget -O $@ https://github.com/yui/yuicompressor/releases/download/v$(YUICOMPRESSOR_VERSION)/$(notdir $@)

$(HTMLCOMPRESSOR):
	wget -O $@ http://htmlcompressor.googlecode.com/files/$(notdir $@)


.PHONY: touch clean
.DELETE_ON_ERROR:
