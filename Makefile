all: public

public:
	@python ./bin/build.py $@

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

.tmp/%.css: src/%.css
	@echo " MIN  $@"
	@exec mkdir -p $(dir $@)
	exec curl -X POST -s --data-urlencode "input@$<" \
		https://cssminifier.com/raw >$@

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
