STATIC	= $(addprefix public/d/,$(notdir $(wildcard src/*.*))) \
	  $(patsubst static/%,public/%,$(wildcard static/*.*) \
	                               $(wildcard static/*/*.*)) \
	  public/.htaccess

YUICOMPRESSOR_VERSION = 2.4.8
YUICOMPRESSOR = bin/yuicompressor-$(YUICOMPRESSOR_VERSION).jar


all: public
.PHONY: all


touch:
	touch src/*.* src/data/*.*

clean:

distclean: clean
	-rm -r public

.PHONY: touch clean distclean


public/d/%.js: src/%.js $(YUICOMPRESSOR)
	@exec sh bin/compressor.sh $@ $^

public/d/%.css: src/%.css $(YUICOMPRESSOR) $(wildcard src/data/*.*)
	@exec sh bin/compressor.sh $@ $< $(YUICOMPRESSOR) src/data

public/%: static/%
	@exec mkdir -p $(dir $@)
	@echo " CP   $(notdir $@)"
	@exec cp -- $< $@

public/%.gz: public/%
	@echo " GZ   $(notdir $<)"
#	@exec gzip -9 <$< >$@
	@exec zopfli -c $< >$@

public/.htaccess: src/htaccess
	@echo " CP   $(notdir $<)"
	@exec cp -- $< $@


static: $(STATIC)
.PHONY: static


compress-public: $(addsuffix .gz,$(shell \
	find public -name '*.xml' -o -name '*.html' -o \
	            -name '*.css' -o -name '*.js'))

public: static
	@exec python bin/build-site.py
# We run another make process so that it rereads the Makefile and most
# importantly re-runs all of the $(shell find …) substitutions since when this
# recipe is executed contents of .tmp has been refreshed.
	@$(MAKE) compress-public

upload: public
	@echo " UP"
	@rsync -mrltvze ssh --delete-after \
	       --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r \
	       --progress $^ nfs:/home/

upload-files:
	@echo " UP"
	@rsync -mrltvze ssh --delete-after \
	       --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r --progress \
	       files/ static/favicon.ico static/robots.txt \
	       files86:/home/public


.PHONY: .tmp tmp-to-public compress-public public upload upload-files


$(YUICOMPRESSOR):
	wget -O $@ https://github.com/yui/yuicompressor/releases/download/v$(YUICOMPRESSOR_VERSION)/$(notdir $@)


.DELETE_ON_ERROR:
