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
import io
import datetime
import gzip
import itertools
import jinja2
import os
import re
import subprocess
import sys
import tempfile

import compilers
import paths


HOST = 'mina86.com'
BASE_HREF = 'https://' + HOST

NOW = datetime.datetime.utcnow()

POSTS_SUBDIR = paths.POSTS_SUBDIR
PAGES_SUBDIR = paths.PAGES_SUBDIR
TPL_SUBDIR = paths.TPL_SUBDIR

REPO_URL = paths.REPO_URL

SUPPORTED_LANGUAGES = ('en', 'pl')


TRANSLATIONS = {
    # Category names
    'Everything': {'pl': 'Wszystko'},
    'Articles': {'pl': 'Artykuły'},
    'Downloads': {'pl': 'Do pobrania'},
    'English': {'pl': 'Po angielsku'},
    'Games': {'pl': 'Gry'},
    'Misc': {'pl': 'Różne'},
    'Reviews': {'pl': 'Recenzje'},
    'Site News': {'pl': 'Aktualności'},

    # Pagination
    'Page %d': {'pl': '%d. strona'},
    'Older entries': {'pl': 'Starsze wpisy'},
    'Newer entries': {'pl': 'Nowsze wpisy'},

    # Text in templates
    'Contact': {'pl': 'Kontakt'},
    'Categories': {'pl': 'Kategorie'},
    'Atom feed': {'pl': 'Kanał Atom'},

    '<u>p</u>revious:': {'pl': '<u>p</u>oprzedni wpis:'},
    '<u>p</u>revious page': {'pl': '<u>p</u>oprzedna strona'},
    '<u>n</u>ext:': {'pl': '<u>n</u>astępny wpis:'},
    '<u>n</u>ext page': {'pl': '<u>n</u>astępna strona'},

    'Permanent link to the entry.': {'pl': 'Stabilny link do wpisu.'},
    'See comments': {'pl': 'Zobacz komentarze'},
    'Continue reading': {'pl': 'Czytaj dalej'},
    'In categories:': {'pl': 'Kategorie:'},
    'Tagged with:': {'pl': 'Tagi:'},
}


def get_translation(lang, text):
    t = TRANSLATIONS.get(text)
    text = t.get(lang, text) if t else text
    return text.decode('utf-8') if isinstance(text, bytes) else text


MONTHS_PL = (None, 'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
             'lipca', 'sierpnia', 'września', 'października', 'listopada',
             'grudnia')


def format_byline(lang, author, date):
    author = author.replace('<', '&lt').replace('&', '&amp;')

    day = date.day
    month = date.month
    year = date.year
#     month_roman = unichr(0x215F + date.month)

    if lang == 'pl':
        date = '%d %s %d' % (day, MONTHS_PL[month], year)
        fmt = '%s | %s'
    else:
        th = 'th'
        if day < 10 or day > 20:
            th = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        month = date.strftime('%B')
        date = '%d%s of %s %d' % (day, th, month, year)
        fmt = 'Posted by %s on %s'

    return jinja2.utils.Markup(fmt % (author, date))


class _Addresable(object):
    _subdir = None

    @property
    def url(self):
        return '%s%s' % (BASE_HREF, self.href)

    @property
    def href(self):
        if self._subdir:
            return '/%s/%s/' % (self._subdir, self.permalink)
        else:
            return '/%s/' % self.permalink

    def filename_for_lang(self, lang=None):
        args = []
        if self._subdir:
            args.append(self._subdir)
        args.append(self.permalink)
        if lang:
            args.append('index.%s.html' % lang)
        else:
            args.append('index.html')
        return os.path.join(*args)


class _Group(_Addresable, str):

    def __new__(cls, val, date=None):
        self = str.__new__(cls, val.strip())
        self.date = date
        self.entries = []
        return self

    permalink = property(lambda self: re.sub('[^a-z0-9]+', '-', self.lower()))

    def add_entry(self, entry):
        self.entries.append(entry)
        date = entry.latest_date
        if self.date is None or (date is not None and date > self.date):
            self.date = date


class Category(_Group):
    _subdir = 'c'


class Tag(_Group):
    _subdir = 't'


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

    # This is an *ugly*, *ugly* global variable.
    PREFERRED_LANGUAGE = None

    class _Data(collections.namedtuple('PostData', 'subject body date lang')):

        def __new__(cls, d):
            date = d.get('date')
            if date:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            return super(Post._Data, cls).__new__(
                cls,
                subject=d['subject'].strip(),
                body=d['__body__'],
                date=date,
                lang=d['__lang__'])

    def __init__(self, permalink, categories, tags, versions):
        self.permalink = permalink
        self.categories = categories
        self.tags = tags

        versions = [self._Data(ver) for ver in versions]
        self._versions = dict((d.lang, d) for d in versions)
        self._default = (self._versions.get(SUPPORTED_LANGUAGES[0]) or
                         self._versions.get(None) or versions[0])

        date = None
        for d in versions:
            if d.date is not None and (date is None or d.date > date):
                date = d.date
        self.latest_date = date

    def __getattr__(self, attr):
        if attr not in self._Data._fields:
            raise AttributeError(attr)
        d = self._versions.get(self.PREFERRED_LANGUAGE, self._default)
        return getattr(d, attr)

    _subdir = property(lambda self: self.date.strftime('%Y'))


class Page(Post):
    _subdir = None


def parse_filename(filename):
    if (filename[0] == '.' or filename[0] == '#' or
        filename.endswith('.comments')):
        return None

    if filename.endswith('.html'):
        filename = filename[:-5]
    for lang in SUPPORTED_LANGUAGES:
        if filename.endswith('.' + lang):
            return filename[:-len(lang)-1], lang
    else:
        raise ValueError('filename with no language specified: ' + filename)


def read_entry(fd):
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

    d['__body__'] = Body(excerpt, content)
    return d


class Site(object):

    def __init__(self, posts_dir, pages_dir):
        self._categories = {}
        self._tags = {}
        self.posts = list(self._read_entries(posts_dir, Post))
        self.pages = list(self._read_entries(pages_dir, Page))

    categories = property(lambda self: iter(self._categories.values()))
    tags = property(lambda self: iter(self._tags.values()))

    def _read_entries(self, dirname, factory):
        entries = []
        for filename in os.listdir(dirname):
            pl = parse_filename(filename)
            if not pl:
                continue
            permalink, lang = pl

            with codecs.open(os.path.join(dirname, filename),
                             encoding='utf-8') as fd:
                d = read_entry(fd)

            d['__lang__'] = lang
            d['__permalink__'] = permalink
            entries.append(d)

        entries.sort(key=lambda d: d['__permalink__'])
        for permalink, versions in itertools.groupby(
                entries, key=lambda d: d['__permalink__']):
            versions = list(versions)

            kw = {}
            for attr, f in (('categories', Category),
                            ('tags', Tag)):
                groups = set()
                for d in versions:
                    text = d.get(attr)
                    if text:
                        groups.update(t.strip() for t in text.split(','))
                g = getattr(self, '_' + attr)
                kw[attr] = [g.setdefault(t, f(t)) for t in groups]
                kw[attr].sort()

            p = factory(permalink, kw['categories'], kw['tags'], versions)

            for attr, lst in list(kw.items()):
                for group in lst:
                    group.add_entry(p)

            yield p


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
        output = io.StringIO()
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


class Writer(object):

    def __init__(self, writer, tpl_dir, static_mappings):
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_dir),
                                       autoescape=True)
        self._writer = writer
        self._tpl_dir = tpl_dir
        self._static_mappings = static_mappings

    def write_html(self, filename, tpl_name, data):
        data = self._env.get_template(tpl_name + '.html').render(data)
        data = compilers.minify_html(data,
                                     static_mappings=self._static_mappings,
                                     base_href=BASE_HREF + '/')
        self.write_file(filename, data)

    def write_atom(self, filename, entries, href, feed_id, title=None):
        author = ('<author><name>Michał ‘mina86’ Nazarewicz</name>'
                  '<uri>%s</uri></author>' % BASE_HREF)

        def e(val):
            return val.replace('&', '&amp;').replace('<', '&lt;')

        fd = io.StringIO()

        def write(val, **kw):
            val = re.sub('\s+', ' ', val)
            val = re.sub('> <', '><', val)
            val = val.strip()
            if kw:
                kw.setdefault('author', author)
                if 'date' in kw:
                    kw['date'] = kw['date'].strftime('%Y-%m-%dT%H:%M:%SZ')
                val %= kw
            fd.write(val)

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
              title=title + ' — mina86.com' if title else 'mina86.com',
              id=feed_id,
              self_url=e('%s/%s' % (BASE_HREF, filename)),
              page_url=e(BASE_HREF + href),
              date=entries[0].date)
        for entry in entries[:10]:
            write('''
                <entry>
                  <title>%(subject)s</title>
                  <id>%(id)s</id>
                  <link rel="self" href="%(url)s"/>
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
                  lang=entry.lang or 'en',
                  body=e(entry.body.full))
        write('</feed>')

        self.write_file(filename, fd.getvalue())

    def write_file(self, filename, content):
        self._writer.write_file(filename, content)


_KW_LINE_RE = re.compile(r'^<!-- ([a-z]+): (.*) -->')
_KW_SEPARATOR_LINE_RE = re.compile(r'^<!-- ([A-Z]*) -->')


def generate(writer, site):
    sitemap = Sitemap()

    redirs = collections.defaultdict(set)
    redirs_cutoff = datetime.datetime(2016, 5, 1)

    for lang in SUPPORTED_LANGUAGES:
        Post.PREFERRED_LANGUAGE = lang

        T = lambda text: get_translation(lang, text)

        if lang == SUPPORTED_LANGUAGES[0]:
            sitemap_add = sitemap.add
        else:
            sitemap_add = lambda *args, **kw: None

        def write_html(filename, tpl, data):
            data['lang'] = lang
            data['T'] = (
                lambda text: jinja2.utils.Markup(get_translation(lang, text)))
            data['byline'] = (
                lambda author, date: format_byline(lang, author, date))
            writer.write_html(filename, tpl, data)

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
                'desc': T('Everything'),
                'count': len(posts),
                'feed': '/atom',
            }
        ]
        for cat in sorted(site.categories, key=lambda v: T(v).lower()):
            categories.append({
                'href': cat.href,
                'desc': T(cat),
                'count': len(cat.entries),
                'feed': '/c/%s/atom' % cat.permalink,
            })

        # Generate archive pages
        for i in range(len(years)):
            year = years[i]
            write_html('%d/index.%s.html' % (year, lang), 'index', {
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
            sitemap_add('%s/%d/' % (BASE_HREF, year),
                        by_year[year][0].date,
                        'weekly' if year == NOW.year else 'monthly',
                        '0.1')

        # Generate category pages
        for cat in site.categories:
            filename = cat.filename_for_lang(lang)
            entries = sorted(cat.entries, key=lambda p: p.date, reverse=True)
            write_html(filename, 'index', {
                'title': T(cat),
                'canonical': cat.url,
                'entries': entries,
                'archives': archives,
                'categories': categories,
            })
            sitemap_add(cat.url, cat.date, 'weekly', '0.3')

            filename = os.path.join(os.path.dirname(filename),
                                    'atom.%s.xml' % lang)
            feed_id = ('http://mina86.com/atom/cat/%s/content/html/' %
                       cat.permalink)
            writer.write_atom(filename, entries, href=cat.href, feed_id=feed_id,
                              title=T(cat))

        # Generate pagination pages (10 entries per page)
        i = 0
        while i * 10 < len(posts):
            href = lambda p: '/%d' % p if p else '/'
            filename = '%s.%s.html' % (str(i) if i else 'index', lang)
            write_html(filename, 'index', {
                'title': T('Page %d') % i if i else None,
                'canonical': BASE_HREF + href(i),
                'prev': {
                    'href': href(i + 1),
                    'title': T('Older entries')
                } if i * 10 + 10 < len(posts) else None,
                'next': {
                    'href': href(i - 1),
                    'title': T('Newer entries')
                } if i else None,
                'entries': posts[i * 10:i * 10 + 10],
                'archives': archives,
                'categories': categories,
            })
            sitemap_add(BASE_HREF + href(i), posts[i * 10].date,
                        'weekly', '0.4' if i else '1.0')
            i += 1
        writer.write_atom('atom.%s.xml' % lang, posts,
                          href='/',
                          feed_id='http://mina86.com/atom/content/html/')

        # Generate posts pages
        for i in range(len(posts)):
            # next and prev are swapped because posts is reversed
            cur = posts[i]
            write_html(cur.filename_for_lang(lang), 'post', {
                'title': cur.subject,
                'next': posts[i - 1] if i else None,
                'entry': cur,
                'prev': posts[i + 1] if i + 1 < len(posts) else None,
                'canonical': cur.url,
                'archives': archives,
                'categories': categories,
            })
            sitemap_add(cur.url, cur.date, priority='1.0')
            if cur.date < redirs_cutoff:
                redirs[cur.date.year].add(cur.permalink)

        # Generate rewrites in /p directory which for a short while was where
        # all files lived.
        content = ['RewriteEngine On']
        for year in sorted(redirs):
            links = redirs[year]
            if len(links) == 1:
                links = links.pop()
            else:
                links = sorted(links)
                links = '(?:%s)' % '|'.join(links)
            content.append(
                'RewriteRule "^(%s(?:/.*|$))" "/%s/$1" [END,R=permanent]' % (
                    links, year))
        writer.write_file('p/.htaccess', '\n'.join(content))

        # Generate pages pages
        for entry in site.pages:
            write_html(entry.filename_for_lang(lang), 'page', {
                'entry': entry,
                'canonical': entry.url,
                'archives': archives,
                'categories': categories,
            })
            sitemap_add(entry.url, priority='1.0')

    # Finalise with writing out sitemap
    sitemap = sitemap.format()
    writer.write_file('sitemap.xml', sitemap)


def build(writer, static_mappings):
    site = Site(posts_dir=POSTS_SUBDIR, pages_dir=PAGES_SUBDIR)
    writer = Writer(writer, TPL_SUBDIR, static_mappings)
    generate(writer, site)
