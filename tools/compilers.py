# CSS and HTML files pre-processor.                -*- coding: utf-8 -*-
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
import typing

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', 'htmlmin')))
import htmlmin.parser


_MIMETYPES: typing.Dict[str, str] = {
    '.jpg': 'image/jpeg',
    '.png': 'image/png',
    '.svg': 'image/svg+xml',
}


def _encode_base64(mime: str, data: bytes) -> bytes:
    data = base64.standard_b64encode(data)
    return b'data:%s;base64,%s' % (mime.encode('ascii'), data)


def _encode_string(mime: str, data: str, q: str) -> bytes:
    data = data.replace('\n', '\\n').replace(q, '\\' + q)
    return '{}data:{},{}{}'.format(q, mime, data, q).encode('utf-8')


def _insert_data(src_dir: str, path: str) -> bytes:
    _, ext = os.path.splitext(path)
    mime = _MIMETYPES[ext]
    data = open(os.path.join(src_dir, path), 'rb').read()

    encodings = [_encode_base64(mime, data)]
    if ext == '.svg':
        str_data = re.sub(r'[\0-\x1f\x80-\xff%#]',
                          lambda m: '%%%02x' % ord(m.group(0)),
                          data.decode('utf-8').strip())
        encodings.append(_encode_string(mime, str_data, '"'))
        encodings.append(_encode_string(mime, str_data, "'"))
        encodings.sort(key=len)

    return encodings[0]


def _map_static(mappings: typing.Dict[str, str], path: str) -> str:
    return mappings.get(path, path)


def process_css(data: bytes, src_dir: str,
                mappings: typing.Dict[str, str]) -> bytes:
    data = re.sub(rb'DATA<([^<>]+)>',
                  lambda m: _insert_data(src_dir, m.group(1).decode('utf-8')),
                  data)
    data = re.sub(rb'/d/[-_a-zA-Z0-9.]*',
                  lambda m: _map_static(mappings, m.group(0).decode('utf-8')).encode('utf-8'),
                  data)
    return data

_Attributes = typing.Sequence[typing.Tuple[str, typing.Optional[str]]]

class HTMLMinParser(htmlmin.parser.HTMLMinParser):
    @staticmethod
    def _minify_css(data):
        # CSS style, remove unnecessary spaces after punctuation marks.
        # This is very likely to break non-trivial rules.
        data = re.sub(r'\s+', ' ', data.strip())
        return re.sub(r'\s*([:;,{}])\s*', r'\1', data)

    def __init__(self, *args: typing.Any, **kw: typing.Any):
        self._static_mappings = kw.pop('static_mappings', None)
        self._src_dir = kw.pop('src_dir', None)
        super().__init__(*args, **kw)

    def handle_starttag(self, tag: str, attrs: _Attributes) -> None:
        self._transform_attrs(tag, attrs)
        super().handle_starttag(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: _Attributes) -> None:
        self._transform_attrs(tag, attrs)
        super().handle_startendtag(tag, attrs)

    def _transform_attrs(self, tag: str, attrs: _Attributes) -> None:
        for i, (attr, value) in enumerate(attrs):
            if value:
                typing.cast(typing.List, attrs)[i] = (
                    attr, self._transform_attr(tag, attr, value))

    def _transform_attr(self, tag: str, attr: str, value: str) -> str:
        if self._static_mappings:
            ret = self._static_mappings.get(value)
            if ret:
                return ret

        if self._src_dir and tag == 'img' and attr == 'src':
            return _insert_data(self._src_dir, value).decode('utf-8')

        value = re.sub(r'\s+', ' ', value.strip())
        if attr == 'style':
            value = self._minify_css(value)
        elif attr == 'd' and tag == 'path':
            # In SVG’s D attribute of PATH element the only required white-space
            # is between numbers (except space is not necessary before minus
            # sign).
            value = re.sub(r' ?([-a-zA-Z,]) ?', r'\1', value)
        elif '%s %s' % (tag, attr) in ('link media', 'area coords',
                                     'meta content'):
            # Comma separated lists, remove unnecessary spaces around commas.
            value = re.sub(r' ?, ?', ',', value)
        return value

    def handle_data(self, data):
        if self._tag_stack and self._tag_stack[0][0] == 'style':
            self._data_buffer.append(self._minify_css(data))
        else:
            super().handle_data(data)

    def handle_comment(self, comment: str) -> None:
        if comment.startswith('[if '):
            comment = re.sub(
                r'"(/d/[^"]*)"',
                lambda m: self._static_mappings.get(m.group(1), m.group(1)),
                comment)
        super().handle_comment(comment)



def minify_html(data: str, **kw: typing.Any) -> str:
    block = '(?:%s)' % '|'.join((
        'body', 'br', 'col', 'div', 'form', 'h[1-6]', 'head', 'html', 'link',
        'meta', 'p', 'script', 'table', 't[dhr]', 'textarea', 'title', '[ou]l',
        '[A-Z_][A-Z_]*', 'section', 'header', 'aside', 'article', 'nav',
        'footer', 'style',
        # SVG elements:
        'svg', 'rect', 'g',
    ))

    def make_parser(*args: typing.Any, **kwargs: typing.Any) -> HTMLMinParser:
        kwargs.update(kw)
        return HTMLMinParser(*args, **kwargs)

    data = htmlmin.minify(data,
                          remove_comments=True,
                          remove_empty_space=False,
                          remove_all_empty_space=False,
                          reduce_empty_attributes=True,
                          reduce_boolean_attributes=True,
                          remove_optional_attribute_quotes=True,
                          cls=make_parser).strip()

    data = re.sub(r'\s+(</?(?:%s|pre)\b)' % block, r'\1', data)
    data = re.sub(r'(</pre>)\s+', r'\1', data)
    data = re.sub('(<pre>)(?:[ \t]*\n)+', r'\1', data)
    data = re.sub(r'(</?%s\b[^>]*>)\s+' % block, r'\1', data)
    data = re.sub(r'\s+<text\b', '<text', data)

    return data
