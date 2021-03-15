all: public

define copy
$2: $1
	@echo " CP   $$^ → $$@"
	@exec mkdir -p -- $$(@D)
	@exec cp -- $$^ $$@
endef

public: public/www.mina86.com/.htaccess
$(eval $(call copy,src/htaccess/redir.txt,public/www.mina86.com/.htaccess))

public: public/files.mina86.com/.htaccess
$(eval $(call copy,src/htaccess/files.txt,public/files.mina86.com/.htaccess))

DISTCLEAN_DOMAINS := mina86.com www.mina86.com

define handle_alias
public: public/$1
public/$1:
	@echo " LN   www.mina86.com ← $$@"
	@exec mkdir -p -- $$(@D)
	@exec ln -sf -- www.mina86.com $$@
DISTCLEAN_DOMAINS += $1
endef
$(foreach d,mina86.nfshost.com mina86.name nazarewicz.name, \
            $(eval $(call handle_alias,$d)))

public: public/mina86.com
public/mina86.com: static/mina86.pub static/cv/index.html
	@exec python3 ./tools/build.py --make=$(MAKE) $@

touch:
	touch src/*.* src/data/*.*

clean:
	-rm -rf -- .tmp static/cv/index.html

distclean:
	-rm -rf -- .tmp $(foreach d,$(DISTCLEAN_DOMAINS),public/$d)

.tmp/%.js: src/%.js
	@echo " MIN  $@"
	@exec mkdir -p $(@D)
	exec uglifyjs -c unsafe_undefined \
		-m --mangle-props keep_quoted \
		-o $@ $<

.tmp/%.css: src/%.less
	@echo " LESS $@"
	@exec mkdir -p $(@D)
	exec lessc -su=off --math=strict $< $@
	exec cleancss -O2 'mergeSemantically:on;restructureRules:on' -o $@ $@

static/mina86.pub:
	@echo " GPG  $@"
	gpg --armor --export 0x2060401250751FF4 >$@

static/cv/index.html: cv/cv.xml cv/cv.xsl tools/embed-images.py \
                      $(glob cv/*.png) $(glob cv/*.jpg)
	@echo " XSL  $@"
	mkdir -p -- $(@D)
	xsltproc $< | python3 ./tools/embed-images.py cv >$@

%.gz: %
	@echo " GZ   $@"
	exec zopfli -c $< >$@

upload: public
	@echo " UP   *.mina86.com"
	rsync -mrltvze ssh --delete-after --chmod=Du=rwx,Dgo=rx,Fu=rw,Fgo=r \
	       -f'P .well-known/***' --progress $^ nfs:/home/

.DELETE_ON_ERROR:
.PHONY: public public/mina86.com touch clean distclean upload
