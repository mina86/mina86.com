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


_MIMETYPES: typing.Dict[str, bytes] = {
    '.jpg': b'image/jpeg',
    '.png': b'image/png',
    '.svg': b'image/svg+xml',
}

def _encode_base64(mime: bytes, data: bytes) -> bytes:
    data = base64.standard_b64encode(data)
    return b'data:%s;base64,%s' % (mime, data)

def _encode_string(mime: bytes, data: bytes, css: bool) -> bytes:
    chars = r'\0-\x1f\x80-\xff%#'
    if not css:
        # In HTML mode we don’t have to URL escape greater than sign, apostrophe
        # and quote in the string since those can be handled via HTML entities.
        # However, URL encoding is just three-character long while the entities
        # are at least four.
        if data.count(b"'") > data.count(b'"'):
            chars += r' >"'
        else:
            chars += r" >'"

    str_data = re.sub('[{}]'.format(chars),
                      lambda m: '%%%02x' % ord(m.group(0)),
                      data.decode('utf-8').strip())

    def fmt(data: str, quote: str = '') -> bytes:
        quote = quote.encode('ascii')
        return b'%sdata:%s,%s%s' % (quote, mime, data.encode('ascii'), quote)

    if not css:
        return fmt(str_data)

    str_data.replace('\n', '\\n')
    x, y = [fmt(str_data.replace(q, '\\' + q), q) for q in '\'"']
    return x if len(x) < len(y) else y

def _insert_data(src_dir: str, path: str, css: bool = False) -> bytes:
    _, ext = os.path.splitext(path)
    mime = _MIMETYPES[ext]
    data = open(os.path.join(src_dir, path), 'rb').read()

    encoded = _encode_base64(mime, data)
    if ext != '.svg':
        return encoded

    x = encoded
    y = _encode_string(mime, data, css)
    return x if len(x) < len(y) else y


def _map_static(mappings: typing.Dict[str, str], path: str) -> str:
    return mappings.get(path, path)


def process_css(data: bytes, src_dir: str,
                mappings: typing.Dict[str, str]) -> bytes:
    data = re.sub(rb'DATA<([^<>]+)>',
                  lambda m: _insert_data(src_dir, m.group(1).decode('utf-8'),
                                         css=True),
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
        self._self = [[1, kw.pop('self_url', None)]]
        super().__init__(*args, **kw)

    def handle_starttag(self, tag: str, attrs: _Attributes) -> None:
        self._transform_attrs(tag, attrs)
        self._self[-1][0] += 1
        super().handle_starttag(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: _Attributes) -> None:
        self._transform_attrs(tag, attrs)
        if not self._self[-1][0]:
            self._self.pop()
        super().handle_startendtag(tag, attrs)

    def handle_endtag(self, tag):
        self._self[-1][0] -= 1
        if not self._self[-1][0]:
            self._self.pop()
        super().handle_endtag(tag)

    def _transform_attrs(self, tag: str, attrs: _Attributes) -> None:
        i = 0
        while i < len(attrs):
            attr, value = attrs[i]
            if (tag in ('path', 'text', 'use', 'rect', 'circle') and
                attr in ('x', 'cx', 'y', 'cy') and
                value == '0'):
                del attrs[i]
                continue
            if attr == 'self':
                self._self.append([0, value])
                del attrs[i]
                continue
            if value:
                typing.cast(typing.List, attrs)[i] = (
                    attr, self._transform_attr(tag, attr, value))
            i += 1

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
        elif attr in ('href', 'src') and tag != 'base':
            if value.startswith('https://'):
                value = value[6:]
            if value.startswith('//mina86.com/'):
                value = value[12:]
            if value.startswith('/self'):
                s = self._self[-1][1]
                assert s is not None
                value = s + value[5:]
        return value

    def handle_data(self, data):
        if self._tag_stack and self._tag_stack[0][0] == 'style':
            self._data_buffer.append(self._minify_css(data))
            return
        super().handle_data(data)


def _html_tag_re(tag, **kw):
    is_open = kw.get('open')
    is_close = kw.get('close')
    assert not (is_open and is_close)

    fmt = r'</{tag}>' if is_close else r'<{slash}{tag}\b[^>]*>'
    return fmt.format(slash='' if is_open else '/?', tag=tag)


_MINIFY_HTML_RE = re.compile(r'''
      {space} ( {block_tag}  ) {space}?
    |         ( {block_tag}  ) {space}
    | {space} ( {text_open}  )
    |         ( {text_close} ) {space}
    | {space} ( {pre_open}   ) {blank}*
    |         ( {pre_open}   ) {blank}+
    | \s+     ( {pre_close}  ) {space}?
    |         ( {pre_close}  ) {space}
'''.format(
    space=r'\ ',
    blank=r'(?:[ \t]*\n)',

    block_tag=_html_tag_re('(?:%s)' % '|'.join((
        'address', 'article', 'aside', 'base', 'blockquote', 'body', 'br',
        'canvas', 'caption', 'col(?:group)?', 'd[dlt]', 'div',
        'fig(?:caption|ure)', 'footer', 'form', 'h[1-6r]', 'head(?:er)?',
        'hgroup', 'iframe', 'li(?:nk)?', 'main', 'meta', 'nav', 'noscript',
        '[ou]l', 'opt(?:group|ion)', 'p', 'script', 'section', 'style',
        't(?:able|head|body|foot|[dhr]|itle)',

        # SVG elements:
        'svg', 'rect', 'circle', 'g', 'path',
    ))),
    text_open=_html_tag_re('text', open=True),
    text_close=_html_tag_re('text', close=True),
    pre_open='{pre}(?:{code})?'.format(pre=_html_tag_re('pre', open=True),
                                       code=_html_tag_re('code', open=True)),
    pre_close='(?:{code})?{pre}'.format(pre=_html_tag_re('pre', close=True),
                                        code=_html_tag_re('code', close=True)),
), re.VERBOSE)

def minify_html(data: str, **kw: typing.Any) -> str:
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

    def pick_group(m):
        for i in range(1, m.lastindex + 1):
            if (grp := m.group(i)) is not None:
                return grp

    data = _MINIFY_HTML_RE.sub(pick_group, data)

    return data
