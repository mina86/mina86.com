YUICOMPRESSOR_VERSION = 2.4.8
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar

all: public

public:
	@python ./bin/build.py $@

touch:
	touch src/*.* src/data/*.*

clean:
	-rm -r .tmp

distclean:
	-rm -r .tmp public

.tmp/%.js: src/%.js $(YUICOMPRESSOR)
	@echo " MIN  $@"
	exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type js $< >$@

.tmp/%.css: src/%.css $(YUICOMPRESSOR) $(wildcard src/data/*.*)
	@echo " MIN  $@"
	exec mkdir -p $(dir $@)
	exec java -jar $(YUICOMPRESSOR) -v --type css $< >$@

%.gz: %
	@echo " GZ   $@"
	exec zopfli -c $< >$@

upload: public
	@echo " UP   mina86.com"
	rsync -mrltvze ssh --delete-after \
	       --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r \
	       --progress $^ nfs:/home/

upload-files:
	@echo " UP   files.mina86.com"
	rsync -mrltvze ssh --delete-after \
	       --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r --progress \
	       files/ static/favicon.ico static/robots.txt \
	       files86:/home/public

$(YUICOMPRESSOR):
	wget -O $@ https://github.com/yui/yuicompressor/releases/download/v$(YUICOMPRESSOR_VERSION)/$(notdir $@)

.DELETE_ON_ERROR:
.PHONY: all public touch clean distclean upload upload-files
