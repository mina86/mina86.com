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

sys.path.insert(1, os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..', '..', 'htmlmin')))
import htmlmin.parser


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


def _map_static(mappings, m):
    path = m.group(0)
    return mappings.get(path, path)


def process_css(data, src_dir, mappings):
    data = re.sub(r'DATA<([^<>]+)>',
                  lambda m: _insart_data(src_dir, m),
                  data)
    data = re.sub(r'/d/[-_a-zA-Z0-9.]*',
                  lambda m: _map_static(mappings, m),
                  data)
    return data


class HTMLMinParser(htmlmin.parser.HTMLMinParser):

    def __init__(self, *args, **kw):
        self._static_mappings = kw.pop('static_mappings', None)
        htmlmin.parser.HTMLMinParser.__init__(self, *args, **kw)

    def handle_starttag(self, tag, attrs):
        self._transform_attrs(tag, attrs)
        return htmlmin.parser.HTMLMinParser.handle_starttag(self, tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._transform_attrs(tag, attrs)
        return htmlmin.parser.HTMLMinParser.handle_startendtag(self, tag, attrs)

    def _transform_attrs(self, tag, attrs):
        for i, (attr, value) in enumerate(attrs):
            if value:
                attrs[i] = attr, self._transform_attr(tag, attr, value)

    def _transform_attr(self, tag, attr, value):
        ret = self._static_mappings.get(value)
        if ret:
            return ret

        value = re.sub(r'\s+', ' ', value.strip())
        if attr == 'style':
            # CSS style, remove unnecessary spaces after punctuation marks.
            # This is very likely to break non-trivial rules.
            value = re.sub(' ?([:;,]) ', '\\1', value)
        elif '%s %s' % (tag, attr) in ('link media', 'area coords',
                                     'meta content'):
            # Comma separated lists, remove unnecessary spaces around commas.
            value = re.sub(r' ?, ?', ',', value)
        return value

    def handle_comment(self, comment):
        if comment.startswith('[if '):
            comment = re.sub(
                r'"(/d/[^"]*)"',
                lambda m: self._static_mappings.get(m.group(1), m.group(1)),
                comment)
        htmlmin.parser.HTMLMinParser.handle_comment(self, comment)



def minify_html(data, static_mappings):
    block = ('body', 'br', 'col', 'div', 'form', 'h[1-6]', 'head', 'html',
             'link', 'meta', 'p', 'script', 'table', 't[dhr]', 'textarea',
             'title', '[ou]l', '[A-Z_][A-Z_]*', 'section', 'header', 'aside',
             'article', 'nav', 'footer')
    block = '(?:%s)' % '|'.join(block)

    def make_parser(*args, **kw):
        return HTMLMinParser(*args, static_mappings=static_mappings, **kw)

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

    return data