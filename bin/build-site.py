#!/usr/bin/python
# Static blog generator.                           -*- coding: utf-8 -*-
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

import codecs
import collections
import cStringIO
import datetime
import gzip
import itertools
import jinja2
import os
import re
import subprocess
import sys
import tempfile


HOST = 'mina86.com'
BASE_HREF = 'http://' + HOST

NOW = datetime.datetime.utcnow()

POSTS_SUBDIR = 'posts'
PAGES_SUBDIR = 'pages'
TPL_SUBDIR = 'src/tpl'
OUT_SUBDIR = '.tmp'


class _Addresable(object):
    _SUBDIR = None  # must be set by subclass

    @property
    def url(self):
        return '%s/%s' % (BASE_HREF, self.href)

    @property
    def href(self):
        if self._SUBDIR:
            return '/%s/%s/' % (self._SUBDIR, self.permalink)
        else:
            return '/%s/' % self.permalink

    @property
    def filename(self):
        args = []
        if self._SUBDIR:
            args.append(self._SUBDIR)
        args.append(self.permalink)
        args.append('index.html')
        return os.path.join(*args)


class _Group(_Addresable, unicode):
    _SUBDIR = None

    def __new__(cls, val, date=None):
        self = unicode.__new__(cls, val.strip())
        self.date = date
        self.entries = []
        return self

    permalink = property(lambda self: re.sub('[^a-z0-9]+', '-', self.lower()))

    def add_entry(self, entry):
        self.entries.append(entry)
        date = entry.date
        if self.date is None or (date is not None and date > self.date):
            self.date = date


class Category(_Group):
    _SUBDIR = 'c'


class Tag(_Group):
    _SUBDIR = 't'


class Body(object):

    __slots__ = ('excerpt', 'more')

    def __init__(self, excerpt, more):
        self.excerpt = excerpt
        self.more = more

    def __str__(self):
        if self.excerpt:
            return '%s\n%s' % (self.excerpt, self.more)
        return self.more

    short = property(lambda self: self.excerpt or self.more)
    full = property(__str__)


class Post(_Addresable):
    _SUBDIR = 'p'

    def __init__(self, filename, d, excerpt, body):
        if filename.endswith('.html'):
            self.permalink = filename[:-5]
        else:
            self.permalink = filename

        self.subject = d['subject'].strip()

        date = d.get('date')
        if date:
            date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.date = date

        cats = d.get('categories')
        if cats:
            cats = sorted(Category(cat, date) for cat in cats.split(','))
        self.categories = cats

        tags = d.get('tags')
        if tags:
            tags = sorted(Tag(tag, date) for tag in tags.split(','))
        self.tags = tags

        self.body = Body(excerpt, body)

    url = property(lambda self: '%s/p/%s' % (BASE_HREF, self.permalink))


class Page(Post):
    _SUBDIR = None


class Site(object):

    def __init__(self, posts, pages):
        self.posts = posts
        self.pages = pages
        self.categories = self._groups('categories')
        self.tags = self._groups('tags')

    def _groups(self, attr):
        groups = {}
        for entry in self.entries:
            lst = getattr(entry, attr)
            if not lst:
                continue
            for idx, grp in enumerate(lst):
                grp = groups.setdefault(grp, grp)
                grp.add_entry(entry)
                lst[idx] = grp
        groups = set(groups)
        for grp in groups:
            grp.entries.sort(key=lambda entry: entry.date, reverse=True)
        return groups

    entries = property(lambda self: itertools.chain(self.posts, self.pages))
    groups = property(lambda self: itertools.chain(self.categories, self.tags))


class Sitemap(object):

    def __init__(self):
        self._urls = {}

    def add(self, loc, date=None, changefreq=None, priority=None):
        if changefreq is None:
            days = max((NOW - date).days, 0) if date else None
            if days is None or days > 60:
                changefreq = 'monthly'
            else:
                changefreq = 'weekly'

        self._urls[loc] = url = [('loc', loc), ('changefreq', changefreq)]
        if date:
            url.append(('lastmod', date.strftime('%Y-%m-%d')))
        if priority is not None and priority != '0.5':
            url.append(('priority', priority))

    def format(self):
        output = cStringIO.StringIO()
        output.write('<?xml version="1.0" encoding="UTF-8"?><urlset '
                     'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for loc in sorted(self._urls):
            output.write('<url>')
            for tag, val in self._urls[loc]:
                val = val.replace('&', '&amp;').replace('<', '&lt;')
                output.write('<%s>%s</%s>' % (tag, val, tag))
            output.write('</url>')
        output.write('</urlset>')
        return output.getvalue()


def write_file(filename, content):
    if isinstance(content, unicode):
        content = content.encode('utf-8')

    # If file already exists and has the same content, do not overwrite it so
    # that modification date is not affected.
    if os.path.isfile(filename):
        with open(filename) as fd:
            old_content = fd.read()
        if content == old_content:
            return

    with open(filename, 'w') as fd:
        fd.write(content)


class Writer(object):

    def __init__(self, tpl_dir, out_dir):
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_dir),
                                       autoescape=True)
        self._out_dir = out_dir

    def _out_path(self, *args):
        filename = os.path.join(self._out_dir, *args)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return filename

    def write_html(self, filename, tpl_name, data):
        data = self._env.get_template(tpl_name + '.html').render(data)
        write_file(self._out_path(self._out_dir, filename), data)

    def write_atom(self, filename, entries, href, feed_id, title=None):
        author = (u'<author><name>Michał ‘mina86’ Nazarewicz</name>'
                  u'<uri>http://mina86.com/</uri></author>')

        def e(val):
            return val.replace('&', '&amp;').replace('<', '&lt;')

        fd = cStringIO.StringIO()

        def write(val, **kw):
            val = re.sub('\s+', ' ', val)
            val = re.sub('> <', '><', val)
            val = val.strip()
            if kw:
                kw.setdefault('author', author)
                if 'date' in kw:
                    kw['date'] = kw['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
                val %= kw
            fd.write(val.encode('utf-8'))

        write('''
            <?xml version="1.0" encoding="UTF-8"?>
            <feed xmlns="http://www.w3.org/2005/Atom">
                <title>%(title)s</title>
                <id>%(id)s</id>
                <link rel="self" type="application/atom+xml"
                      href="%(self_url)s"/>
                <link href="%(page_url)s"/>
                <updated>%(date)s</updated>
                %(author)s
        ''',
              title=title + u'―mina86.com' if title else 'mina86.com',
              id=feed_id,
              self_url=e('%s/%s' % (BASE_HREF, filename)),
              page_url=e(BASE_HREF + href),
              date=entries[0].date)
        for entry in entries[:10]:
            write('''
                <entry>
                  <title>%(subject)s</title>
                  <id>%(id)s</id>
                  <published>%(date)s</published>
                  <updated>%(date)s</updated>
                  %(author)s
                  <content type="html" xml:lang="%(lang)s"
                           xml:base="%(url)s">%(body)s</content>
                </entry>
            ''',
                  subject=e(entry.subject),
                  id=(entry.date.strftime('http://mina86.com/%Y/%m/%d/') +
                      entry.permalink),
                  url=e(entry.url),
                  date=entry.date,
                  lang='en',
                  body=e(entry.body.full))
        write('</feed>')

        write_file(self._out_path(filename), fd.getvalue())

    def write_file(self, filename, content):
        write_file(self._out_path(filename), content)


_KW_LINE_RE = re.compile(r'^<!-- ([a-z]+): (.*) -->')
_KW_SEPARATOR_LINE_RE = re.compile(r'^<!-- ([A-Z]*) -->')


def read_entry(filename, fd, cls=Post):
    excerpt = None
    content = ''
    kw = d = {}

    for line in fd:
        if kw is not None:
            m = _KW_LINE_RE.search(line)
            if m:
                kw[m.group(1)] = m.group(2)
                continue
            kw = None

        m = _KW_SEPARATOR_LINE_RE.search(line)
        if not m:
            content += line
            continue

        if m.group(1) == 'COMMENT':
            break
        elif m.group(1) == 'EXCERPT':
            excerpt = content
            content = ''
        else:
            sys.stderr.write('Unexpected separator: ' + line)

    return cls(filename, d, excerpt, content)


def read_entries(dirname, cls=Post):
    for name in os.listdir(dirname):
        if name.startswith('.'):
            continue
        with codecs.open(os.path.join(dirname, name), encoding='utf-8') as fd:
            yield read_entry(name, fd, cls)


def generate(writer, site):
    sitemap = Sitemap()

    posts = sorted(site.posts, key=lambda post: post.date, reverse=True)

    # Figure out links to archive pages
    by_year = collections.defaultdict(list)
    for post in posts:
        by_year[post.date.year].append(post)

    archives = []
    years = sorted(by_year, reverse=True)
    for i in range(len(years)):
        year = years[i]
        archives.append({
            'href': '/%d/' % year,
            'desc': str(year),
            'count': len(by_year[year]),
        })

    # Figure out links to category pages
    categories = [
        {
            'href': '/',
            'desc': 'Everything',
            'count': len(posts),
            'feed': '/atom',
        }
    ]
    for cat in sorted(site.categories, key=lambda v: v.lower()):
        categories.append({
            'href': cat.href,
            'desc': cat,
            'count': len(cat.entries),
            'feed': '/c/%s/atom' % cat.permalink,
        })

    # Generate archive pages
    for i in range(len(years)):
        year = years[i]
        writer.write_html('%d/index.html' % year, 'index', {
            'title': str(year),
            'canonical': '%s/%d/' % (BASE_HREF, year),
            'prev': {
                'href': '/%d/' % years[i - 1],
                'title': str(years[i - 1])
            } if i else None,
            'next': {
                'href': '/%d/' % years[i + 1],
                'title': str(years[i + 1])
            } if i + 1 < len(years) else None,
            'entries': by_year[year],
            'archives': archives,
            'categories': categories,
        })
        sitemap.add('%s/%d/' % (BASE_HREF, year),
                    by_year[year][0].date,
                    'weekly' if year == NOW.year else 'monthly',
                    '0.1')

    # Generate category pages
    for cat in site.categories:
        writer.write_html(cat.filename, 'index', {
            'title': cat,
            'canonical': cat.url,
            'entries': cat.entries,
            'archives': archives,
            'categories': categories,
        })
        sitemap.add(cat.url, cat.entries[0].date, 'weekly', '0.3')

        filename = os.path.join(os.path.dirname(cat.filename), 'atom.xml')
        feed_id = 'http://mina86.com/atom/cat/%s/content/html/' % cat.permalink
        writer.write_atom(filename, cat.entries,
                          href=cat.href, feed_id=feed_id,
                          title=cat)

    # Generate pagination pages (10 entries per page)
    i = 0
    while i * 10 < len(posts):
        href = lambda p: '/%d.html' % p if p else '/'
        writer.write_html('%d.html' % i if i else 'index.html', 'index', {
            'title': 'Page %d' % i if i else None,
            'canonical': BASE_HREF + href(i),
            'prev': {
                'href': href(i + 1),
                'title': 'Older entries'
            } if i * 10 + 10 < len(posts) else None,
            'next': {
                'href': href(i - 1),
                'title': 'Newer entries'
            } if i else None,
            'entries': posts[i * 10:i * 10 + 10],
            'archives': archives,
            'categories': categories,
        })
        sitemap.add(BASE_HREF + href(i), posts[i * 10].date,
                    'weekly', '0.4' if i else '1.0')
        i += 1
    writer.write_atom('atom.xml', posts,
                      href='/', feed_id='http://mina86.com/atom/content/html/')

    # Generate posts pages
    for i in range(len(posts)):
        # next and prev are swapped because posts is reversed
        cur = posts[i]
        writer.write_html(cur.filename, 'post', {
            'title': cur.subject,
            'next': posts[i - 1] if i else None,
            'entry': cur,
            'prev': posts[i + 1] if i + 1 < len(posts) else None,
            'canonical': cur.url,
            'archives': archives,
            'categories': categories,
        })
        sitemap.add(cur.url, cur.date, priority='1.0')

    # Generate pages pages
    for entry in site.pages:
        writer.write_html(entry.filename, 'page', {
            'entry': entry,
            'canonical': entry.url,
            'archives': archives,
            'categories': categories,
        })
        sitemap.add(entry.url, priority='1.0')

    # Finalise with writing out sitemap
    sitemap = sitemap.format()
    writer.write_file('sitemap.xml', sitemap)


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    out_dir = os.path.join(root_dir, OUT_SUBDIR)

    posts = list(read_entries(os.path.join(root_dir, POSTS_SUBDIR)))
    pages = list(read_entries(os.path.join(root_dir, PAGES_SUBDIR), cls=Page))
    site = Site(posts, pages)

    writer = Writer(os.path.join(root_dir, TPL_SUBDIR), out_dir)
    generate(writer, site)


if __name__ == '__main__':
    main()
