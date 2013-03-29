#!/bin/sh
# XML code optimiser.
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

add_note=
if [ x"$1" = x--add-note ]; then
	shift
fi

if [ -n "$3" ]; then
	htmlcompressor_jar=$3
	htmlcompressor() {
		java -jar "$htmlcompressor_jar" -t html \
			--remove-quotes \
			--simple-doctype \
			--remove-style-attr \
			--remove-link-attr \
			--remove-script-attr \
			--remove-form-attr \
			--remove-input-attr \
			--simple-bool-attr \
			"$1"
	}
else
	htmlcompressor() {
		cat "$1"
	}
fi


tmp="$2~$$~filter~"
trap 'rm -f -- "$tmp"' 0

block='\(body\|br\|col\|div\|form\|h[1-6]\|head\|html\|link\|meta\|p\|script\|table\|t[dhr]\|textarea\|title\|[ou]l\|[A-Z_][A-Z_]*\|section\|header\|aside\|article\|nav\|footer\)'
htmlcompressor "$1" | sed >$tmp -n -e "
	H
	\$ {
		x
		s/[[:space:]][[:space:]]*/ /g
		s/^ \\| \$//g
		s~ \\(</\\?$block\\)~\\1~g
		s~\\(<$block\\( [^>]*\\)\\?>\\) ~\\1~g
		s~ \\?<li~ <li~g
		s~ <link~<link~g
		$add_note
		p
	}
"

mv -f -- "$tmp" "$2"
