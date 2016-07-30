# CSS files pre-processor.                         -*- coding: utf-8 -*-
# Copyright 2016 by Michał Nazarewicz <mina86@mina86.com>
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
# Unless required  by applicable law  or agreed to in  writing, software
# distributed  under the  Apache License  is distributed  on an  "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the  Apache License for the  specific language governing
# permissions and limitations under the License.

import base64
import os
import re
import sys


_MIMETYPES = {
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
}


def _encode_base64(mime, data):
    data = base64.standard_b64encode(data)
    return 'data:%s;base64,%s' % (mime, data)


def _encode_string(mime, data, q):
    data = data.replace('\n', '\\n').replace(q, '\\' + q)
    return '%sdata:%s,%s%s' % (q, mime, data, q)


def _insart_data(src_dir, m):
    path = m.group(1)

    _, ext = os.path.splitext(path)
    mime = _MIMETYPES[ext]
    data = open(os.path.join(src_dir, path)).read()

    encodings = [_encode_base64(mime, data)]
    if ext == '.svg':
        data = re.sub(r'[\0-\x1f\x80-\xff%#]',
                      lambda m: '%%%02x' % ord(m.group(0)),
                      data.strip())
        encodings.append(_encode_string(mime, data, '"'))
        encodings.append(_encode_string(mime, data, "'"))
        encodings.sort(key=len)

    return encodings[0]


def handle(data, src_dir):
    return re.sub(r'DATA<([^<>]+)>',
                  lambda m: _insart_data(src_dir, m),
                  data)


if __name__ == '__main__':
    sys.stderr.write(', '.join(sys.argv))
    _, src_dir = sys.argv
    sys.stdout.write(handle(sys.stdin.read(), src_dir))
