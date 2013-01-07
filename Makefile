ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

all: $(ALL)

touch:
	touch src/*


out/%.js: src/%.js
	@exec mkdir -p $(dir $@)
	exec java -jar bin/yuicompressor.jar -v --type js -o $@ $^

out/%.css: src/%.css
	@exec mkdir -p $(dir $@)
	exec java -jar bin/yuicompressor.jar -v --type css -o $@ $^

out/%.html: src/%.html
	@exec mkdir -p $(dir $@)
	exec sh bin/xml-filter.sh $^ $@

out/%.xml: src/%.xml
	@exec mkdir -p $(dir $@)
	exec sh bin/xml-filter.sh $^ $@


.PHONY: touch
