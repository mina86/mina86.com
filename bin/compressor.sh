#!/bin/sh
# Code minifier.
# Copyright 2012-2013 by Michał Nazarewicz <mina86@mina86.com>
#
# Licensed under the Apache License,  Version 2.0 (the "License"); you
# may not  use this file except  in compliance with the  License.  You
# may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law  or agreed to in writing, software
# distributed under  the License is  distributed on an "AS  IS" BASIS,
# WITHOUT  WARRANTIES OR  CONDITIONS OF  ANY KIND,  either express  or
# implied.   See  the  License  for the  specific  language  governing
# permissions and limitations under the License.

set -e

in=$1
out=$2
jar=$3

tmp="$2~$$~compressor~"
trap 'rm -f -- "$tmp"' 0

run () {
	echo '    ' "$@" >&2
	"$@"
}

echo " ### ${out##*/}"
mkdir -p "${out%/*}"

case $1 in
*.js)
	echo -n '/*See github.com/mina86/mina86.com */' >$tmp
	run java -jar "$jar" -v --type js "$in" >>$tmp
	;;
*.css)
	echo -n '/*See github.com/mina86/mina86.com */' >$tmp
	run java -jar "$jar" -v --type css "$in" >>$tmp
	;;
*.html)
	run java -jar "$jar" -t html \
		--remove-quotes \
		--simple-doctype \
		--remove-style-attr \
		--remove-link-attr \
		--remove-script-attr \
		--remove-form-attr \
		--remove-input-attr \
		--simple-bool-attr \
		"$in" >$tmp
	echo "     sed -n -e ... -i $tmp" >&2
	sed -n -e "
		H
		\$ {
			x
			s/[[:space:]][[:space:]]*/ /g
			s/^ \\| \$//g
			s~ \\(</\\?$block\\)~\\1~g
			s~\\(<$block\\( [^>]*\\)\\?>\\) ~\\1~g
			s~ \\?<li~ <li~g
			s~ <link~<link~g
			s~^<!DOCTYPE[^>]*>~&<!--See github.com/mina86/mina86.com -->~
			p
		}
	" -i "$tmp"
	;;
*)
	echo "Don't know what to do with $in" >&2
	exit 1
esac

mv -f -- "$tmp" "$out"
