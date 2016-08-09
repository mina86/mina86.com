all: public

public: static/mina86.gpg
	@+python ./bin/build.py $@

touch:
	touch src/*.* src/data/*.*

clean:
	-rm -r .tmp

distclean:
	-rm -r .tmp public

.tmp/%.js: src/%.js
	@echo " MIN  $@"
	@exec mkdir -p $(dir $@)
	exec curl -X POST -s --data-urlencode "input@$<" \
		https://javascript-minifier.com/raw >$@

.tmp/%.css: src/%.less
	@echo " LESS $@"
	@exec mkdir -p $(dir $@)
	exec lessc -su=on  $< | cleancss --semantic-merging >$@

static/mina86.gpg:
	@echo " GPG  $@"
	gpg --armor --export 0x2060401250751FF4 >$@

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

.DELETE_ON_ERROR:
.PHONY: all public touch clean distclean upload upload-files
