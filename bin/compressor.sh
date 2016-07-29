#!/bin/sh
# Code minifier.
# Copyright 2012-2013 by Michał Nazarewicz <mina86@mina86.com>
#
# This program is  free software: you can redistribute  it and/or modify
# it under the  terms of the GNU General Public  License as published by
# the Free Software Foundation, either version  3 of the License, or (at
# your option) any later version.
#
# This program  is distributed in the  hope that it will  be useful, but
# WITHOUT   ANY  WARRANTY;   without  even   the  implied   warranty  of
# MERCHANTABILITY  or FITNESS  FOR A  PARTICULAR PURPOSE.   See the  GNU
# General Public License for more details.
#
# You should  have received  a copy  of the  GNU General  Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# Unless required  by applicable law  or agreed to in  writing, software
# distributed  under the  Apache License  is distributed  on an  "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the  Apache License for the  specific language governing
# permissions and limitations under the License.

set -e

out=$1
in=$2
jar=$3
shift 3

tmp="$out~$$~compressor~"
trap 'rm -f -- "$tmp"' 0

run () {
	#echo '    ' "$@" >&2
	"$@"
}

echo " MIN  $out"
mkdir -p "${out%/*}"

case $in in
*.js)
	echo '// github.com/mina86/mina86.com' >$tmp
	run java -jar "$jar" -v --type js "$in" >>$tmp
	;;
*.css)
	echo -n '/* github.com/mina86/mina86.com */' >$tmp
	run java -jar "$jar" -v --type css "$in" | \
		perl ./bin/data-uri.pl "$@" >>$tmp
	;;
*)
	echo "Don't know what to do with $in" >&2
	exit 1
esac

mv -f -- "$tmp" "$out"
