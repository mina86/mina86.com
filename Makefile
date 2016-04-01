ALL	= $(addprefix public/d/,$(notdir $(wildcard src/*.*) \
	                                 $(wildcard static/*.*))) \
	  $(addprefix public/,$(notdir $(wildcard root/*.*)))

YUICOMPRESSOR_VERSION = 2.4.8
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar

HTMLCOMPRESSOR_VERSION = 1.5.3
HTMLCOMPRESSOR = bin/htmlcompressor-$(HTMLCOMPRESSOR_VERSION).jar


all: $(ALL)

touch:
	touch src/*.* src/data/*.*

clean:
	-rm -r public


public/d/%.js: src/%.js $(YUICOMPRESSOR)
	@exec sh bin/compressor.sh $@ $^

public/d/%.css: src/%.css $(YUICOMPRESSOR) $(wildcard src/data/*.*)
	@exec sh bin/compressor.sh $@ $^

public/d/%: static/%
	@exec mkdir -p $(dir $@)
	@echo " CP  $(notdir $@)"
	@exec cp -- $< $@

public/%: root/%
	@exec mkdir -p $(dir $@)
	@echo " CP  $(notdir $@)"
	@exec cp -- $< $@


$(YUICOMPRESSOR):
	wget -O $@ https://github.com/yui/yuicompressor/releases/download/v$(YUICOMPRESSOR_VERSION)/$(notdir $@)

$(HTMLCOMPRESSOR):
	wget -O $@ http://htmlcompressor.googlecode.com/files/$(notdir $@)


.PHONY: touch clean
.DELETE_ON_ERROR:
