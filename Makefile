ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

YUICOMPRESSOR_VERSION = 2.4.7
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar


all: $(ALL)

touch:
	touch src/*

clean:
	-rm -r out


out/%.js: src/%.js $(YUICOMPRESSOR)
	@exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type js -o $@ $<

out/%.css: src/%.css $(YUICOMPRESSOR)
	@exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type css -o $@ $<

out/%.html: src/%.html
	@exec mkdir -p $(dir $@)
	exec sh bin/xml-filter.sh $< $@

out/%.xml: src/%.xml
	@exec mkdir -p $(dir $@)
	exec sh bin/xml-filter.sh $< $@


bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar: bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip
	unzip -j $< -d $(dir $@) yuicompressor-$(YUICOMPRESSOR_VERSION)/build/yuicompressor-$(YUICOMPRESSOR_VERSION).jar
	touch $@

bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip:
	wget -O $@ https://github.com/downloads/yui/yuicompressor/$(notdir $@)


.PHONY: touch clean
.DELETE_ON_ERROR:
.INTERMEDIATE: bin/yuicompressor-$(YUICOMPRESSOR_VERSION).zip
