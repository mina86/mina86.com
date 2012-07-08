ALL	= $(addprefix out/,$(notdir $(wildcard src/*.*)))

all: $(ALL)

touch:
	cd .. && touch $(ALL)


out/%.js: src/%.js
	exec java -jar bin/yuicompressor.jar -v --type js -o $@ $^

out/%.css: src/%.css
	exec java -jar bin/yuicompressor.jar -v --type css -o $@ $^

out/%.html: src/%.html
	exec sh bin/xml-filter.sh $^ $@

out/%.xml: src/%.xml
	exec sh bin/xml-filter.sh $^ $@


.PHONY: touch
