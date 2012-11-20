#!/bin/sh

set -e

tmp="$2~$$~filter~"
trap 'rm -f -- "$tmp"' 0

block='\(body\|br\|col\|div\|form\|h[1-6]\|head\|html\|link\|meta\|p\|script\|table\|t[dhr]\|textarea\|title\|[ou]l\|[A-Z_][A-Z_]*\)'

sed -n -e "
	H
	$ {
		x
		s/<!--[^-]*-->//g
		s/[[:space:]][[:space:]]*/ /g
		s/^ \\| $//g
		s~ \\(</\\?$block\\)~\\1~g
		s~\\(<$block\\( [^>]*\\)\\?>\\) ~\\1~g
		s~ \\?<li~ <li~g
		p
	}
" <$1 >$tmp

mv -f -- "$tmp" "$2"
