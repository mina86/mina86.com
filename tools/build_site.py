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


BASE_HREF = 'https://mina86.com'

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
    'In English': {'pl': 'Po angielsku'},
    'In Polish': {'pl': 'Po polsku'},
    'Misc': {'pl': 'Różne'},
    'Reviews': {'pl': 'Recenzje'},
    'Site News': {'pl': 'Aktualności'},

    # Pagination
    '{} page': {'pl': '{} strona'},
    'Older entries': {'pl': 'Starsze wpisy'},
    'Newer entries': {'pl': 'Nowsze wpisy'},

    # Text in templates
    'Contact': {'pl': 'Kontakt'},
    'Categories': {'pl': 'Kategorie'},

    'older posts': {'pl': 'starsze wpisy'},
    'newer posts': {'pl': 'nowsze wpisy'},

    'Permanent link to the entry.': {'pl': 'Stabilny link do wpisu.'},
    'See comments': {'pl': 'Zobacz komentarze'},
    'Continue reading': {'pl': 'Czytaj dalej'},
    'In categories:': {'pl': 'Kategorie:'},
    'Tagged with:': {'pl': 'Tagi:'},

    'Resume': {'pl': 'CV'},
}


def get_translation(lang, text):
    t = TRANSLATIONS.get(text)
    text = t.get(lang, text) if t else text
    return text.decode('utf-8') if isinstance(text, bytes) else text


def format_ordinal(lang, num):
    if lang == 'pl':
        th = '.'
    elif 4 <= num % 100 <= 20 or 3 < num % 10:
        th = 'th'
    else:
        th = ('th', 'st', 'nd', 'rd')[num % 10]
    return str(num) + th


def format_page_title(*, lang, title, page):
    if not page:
        return title
    page = get_translation(lang, '{} page').format(
        format_ordinal(lang, page + 1))
    if title:
        return '{} ({})'.format(title, page)
    else:
        return page


MONTHS_PL = (None, 'stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
             'lipca', 'sierpnia', 'września', 'października', 'listopada',
             'grudnia')


def format_byline(lang, author, email, date):
    author = author.replace('&', '&amp;').replace('<', '&lt')

    day = date.day
    month = date.month
    year = date.year
#     month_roman = unichr(0x215F + date.month)

    if lang == 'pl':
        date = '%d %s %d' % (day, MONTHS_PL[month], year)
        fmt = '%s | %s'
    else:
        day = format_ordinal('en', day)
        month = date.strftime('%B')
        date = '%s of %s %d' % (day, month, year)
        fmt = 'Posted by %s on %s'

    return jinja2.utils.markupsafe.Markup(fmt % (author, date))


class _Addresable(object):
    _subdir = None

    class __Paged(str):
        def __call__(self, *, page=None):
            return self + str(page) if page else self

    @property
    def url(self):
        return self.__Paged(BASE_HREF + self.href)

    @property
    def href(self):
        if self._subdir:
            href = '/%s/%s/' % (self._subdir, self.permalink)
        else:
            href = '/%s/' % self.permalink
        return self.__Paged(href)

    def filename(self, *, lang=None, page=None):
        args = []
        if self._subdir:
            args.append(self._subdir)
        args.append(self.permalink)
        if page:
            base = str(page)
        else:
            base = 'index'
        if lang:
            args.append('{}.{}.html'.format(base, lang))
        else:
            args.append('{}.html'.format(base))
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

    @property
    def lang(self):
        return {'In English': 'en', 'In Polish': 'pl'}.get(self)


class Tag(_Group):
    _subdir = 't'


class Body(object):
    __slots__ = ('__data', 'excerpt_needs_math', 'full_needs_math')

    def __init__(self, prefix, excerpt_only, rest, needs_math=False):
        if prefix:
            self.__data = (prefix + excerpt_only, prefix + rest)
        else:
            self.__data = (rest, rest)
        if needs_math and prefix:
            p = self.__check_math(prefix)
            self.excerpt_needs_math = p or self.__check_math(excerpt_only)
            self.full_needs_math = p or self.__check_math(rest)
        else:
            needs_math = needs_math and self.__check_math(rest)
            self.excerpt_needs_math = self.full_needs_math = needs_math

    def html(self, full=True):
        return jinja2.utils.markupsafe.Markup(self.__data[full])

    def __str__(self):
        return self.__data[1]

    has_excerpt = property(lambda self: self.__data[0] is not self.__data[1])

    @staticmethod
    def __check_math(text):
        return '\\(' in text or '$$' in text


class Post(_Addresable):

    # This is an *ugly*, *ugly* global variable.
    PREFERRED_LANGUAGE = None

    class _Data(collections.namedtuple('PostData',
                                       'subject body date updated lang')):

        def __new__(cls, d):
            date = d.get('date')
            if date:
                date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            updated = d.get('updated')
            if updated:
                updated = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            return super(Post._Data, cls).__new__(
                cls,
                subject=d['subject'].strip(),
                body=d['__body__'],
                date=date,
                updated=updated,
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
    if not filename.endswith('.html'):
        return None
    filename = filename[:-5]
    for lang in SUPPORTED_LANGUAGES:
        if filename.endswith('.' + lang):
            return filename[:-len(lang)-1], lang
    else:
        raise ValueError('filename with no language specified: ' + filename)


_DIRECTIVE_LINE_RE = re.compile(r'^<!-- (?:'
    r'(?P<key>[a-z]+): (?P<value>.*)'
    r'|(?P<sep>[A-Z ]*)'
    r'|INCLUDE(?P<esc> ESCAPED)?: (?P<inc>[-a-zA-Z0-9.]+)) -->')

def read_entry(fd, dirname):
    parts = ['']
    kw = d = {}

    for line in fd:
        m = _DIRECTIVE_LINE_RE.search(line)
        m = m and m.groupdict()

        if kw is not None:
            if m and m['key']:
                kw[m['key']] = m['value']
                continue
            kw = None

        if not m:
            parts[-1] += line

        elif m['inc']:
            path = os.path.join(dirname, m['inc'])
            with codecs.open(path, encoding='utf-8') as rd:
                data = rd.read()
            if m['esc']:
                data = data.replace('&', '&amp;').replace('<', '&lt;')
            parts[-1] += data

        elif m['sep'] == 'COMMENT':
            break
        elif m['sep'] == 'EXCERPT ONLY':
            if len(parts) == 1:
                parts.append('')
            else:
                sys.stderr.write('Unexpected ‘EXCERPT ONLY’ directive, '
                                 'ignoring')
        elif m['sep'] == 'FULL':
            if len(parts) < 3:
                parts.extend([''] * (3 - len(parts)))
            else:
                sys.stderr.write('Unexpected ‘FULL’ directive, ignoring')
        else:
            sys.stderr.write('Unexpected directive: ' + line)

    if len(parts) == 1:
        parts = ('', '', parts[0])
    elif len(parts) == 2:
        sys.stderr.write('Got ‘EXCERPT ONLY’ without ‘FULL’ directive')
        parts.append('')
    d['__body__'] = Body(*parts, needs_math=d.pop('math', None) == 'true')
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
                d = read_entry(fd, dirname)

            d['__lang__'] = lang
            d['__permalink__'] = permalink
            entries.append(d)

        entries.sort(key=lambda d: d['__permalink__'])
        for permalink, versions in itertools.groupby(
                entries, key=lambda d: d['__permalink__']):
            versions = list(versions)
            langs = frozenset(d['__lang__'] for d in versions)

            kw = {}
            for attr, f in (('categories', Category),
                            ('tags', Tag)):
                groups = set()
                for d in versions:
                    text = d.get(attr)
                    if text:
                        groups.update(t.strip() for t in text.split(','))

                if attr == 'categories' and factory == Post:
                    if 'en' in langs:
                        groups.add('In English')
                    if 'pl' in langs:
                        groups.add('In Polish')

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
    @classmethod
    def _do_striptags(cls, value):
        if hasattr(value, "__html__"):
            value = value.__html__()
        value = str(value).replace('LCh<sub>ab</sub>', 'LCh(ab)')
        value = str(value).replace('LCh<sub>uv</sub>', 'LCh(uv)')
        return jinja2.filters.do_striptags(value)

    def __init__(self, writer, tpl_dir, static_mappings):
        self._env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_dir),
                                       autoescape=True)
        self._env.filters['striptags'] = self._do_striptags

        self._writer = writer
        self._tpl_dir = tpl_dir
        self._static_mappings = static_mappings

    def write_html(self, filename, tpl_name, data):
        data = self._env.get_template(tpl_name + '.html').render(data)
        data = compilers.minify_html(
            data, static_mappings=self._static_mappings)
        self.write_file(filename, data)

    def write_atom(self, filename, entries, href, feed_id, title=None):
        author = ('<author><name>Michał ‘mina86’ Nazarewicz</name>'
                  '<uri>%s</uri></author>' % BASE_HREF)

        def e(val):
            return val.replace('&', '&amp;').replace('<', '&lt;')

        fd = io.StringIO()

        def write(val, **kw):
            val = re.sub('\s+', ' ', val)
            if kw:
                kw.setdefault('author', author)
                for key in ('date', 'updated'):
                    if (value := kw.get(key)) is not None:
                        kw[key] = value.strftime('%Y-%m-%dT%H:%M:%SZ')
                val %= kw
            fd.write(val.replace('> <', '><').strip())

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
              title=title + ' — mina86.com' if title else 'mina86.com',
              id=feed_id,
              self_url=e('%s/%s' % (BASE_HREF, filename)),
              page_url=e(BASE_HREF + href),
              date=entries[0].date)
        for entry in entries[:10]:
            body = str(entry.body)
            if entry.body.full_needs_math:
                if entry.lang == 'pl':
                    msg = ('Ten wpis zawiera formuły matematyczne, które mogą '
                           'zostać niepoprawnie wyświetlone w Twoim czytniku. '
                           'Zalecane jest czytanie <a href="#m">tego artykułu '
                           'na stronie internetowej</a>.')
                else:
                    msg = ('This entry includes Maths formulæ which may be '
                           'rendered incorrectly by your feed reader. You may '
                           'prefer reading <a href="#m">it on the web</a>.')
                body = ('<script defer src={src}></script>'
                        '<p><small>{msg}</small>{body}').format(
                            src=('https://cdn.jsdelivr.net'
                                 '/npm/mathjax@3/es5/tex-chtml.js'),
                            msg=msg,
                            body=body)
            write('''
                <entry xml:base="%(url)s">
                  <title>%(subject)s</title>
                  <id>%(id)s</id>
                  <link rel="alternate" type="text/html" href="%(url)s"/>
                  <published>%(date)s</published>
                  <updated>%(updated)s</updated>
                  %(author)s
                  <content type="html" xml:lang="%(lang)s">%(body)s</content>
                </entry>
            ''',
                  subject=e(entry.subject),
                  id=(entry.date.strftime('http://mina86.com/%Y/%m/%d/') +
                      entry.permalink),
                  url=e(entry.url),
                  date=entry.date,
                  updated=entry.updated or entry.date,
                  lang=entry.lang,
                  body=e(compilers.minify_html(
                      body, static_mappings=self._static_mappings,
                      self_url='')))
        write('</feed>')

        self.write_file(filename, fd.getvalue())

    def write_file(self, filename, content):
        self._writer.write_file(filename, content)

    def link(self, src, dst):
        self._writer.link(src, dst)


def generate(writer, site):
    sitemap = Sitemap()

    redirs = collections.defaultdict(set)

    for lang in SUPPORTED_LANGUAGES:
        Post.PREFERRED_LANGUAGE = lang

        T = lambda text: get_translation(lang, text)

        if lang == SUPPORTED_LANGUAGES[0]:
            sitemap_add = sitemap.add
        else:
            sitemap_add = lambda *args, **kw: None

        def write_html(filename, tpl, data):
            data['lang'] = lang
            data['T'] = lambda text: jinja2.utils.markupsafe.Markup(
                get_translation(lang, text))
            data['byline'] = lambda author, email, date: format_byline(
                lang, author, email, date)
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
        def cat_sort_key(cat):
            cat_lang = cat.lang
            if cat_lang == lang:
                lang_key = 0
            elif cat_lang:
                lang_key = 1
            else:
                lang_key = 2
            return (lang_key, -len(cat.entries), T(cat).lower())
        categories = [{
                'href': '/',
                'desc': T('Everything'),
                'count': len(posts),
                'feed': '/atom',
        }] + [{
            'href': cat.href,
            'desc': T(cat),
            'count': len(cat.entries),
            'feed': '/c/%s/atom' % cat.permalink,
            'lang': cat.lang,
        } for cat in sorted(site.categories, key=cat_sort_key)]

        # Generate archive pages
        for i in range(len(years)):
            year = years[i]
            write_html('%d/index.%s.html' % (year, lang), 'index', {
                'title': str(year),
                'canonical': '/{}/'.format(year),
                'prev': {
                    'href': '/{}/'.format(years[i - 1]),
                    'title': str(years[i - 1])
                } if i else None,
                'next': {
                    'href': '/{}/'.format(years[i + 1]),
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

        def generate_pages(*, entries, href, filename, title=None):
            for idx in range(0, len(entries), 10):
                page = idx // 10
                write_html(filename(lang=lang, page=page), 'index', {
                    'title': format_page_title(
                        lang=lang, title=title, page=page),
                    'canonical': href(page=page),
                    'prev': {
                        'href': href(page=page + 1),
                        'title': T('Older entries')
                    } if idx + 10 < len(entries) else None,
                    'next': {
                        'href': href(page=page - 1),
                        'title': T('Newer entries')
                    } if page else None,
                    'entries': entries[idx:idx + 10],
                    'archives': archives,
                    'categories': categories,
                })
                if not title and not page:
                    changefreq = 'daily'
                    priority = '1.0'
                else:
                    changefreq = 'weekly'
                    priority = '0.3' if title else '0.5'
                sitemap_add(BASE_HREF + href(page=page), entries[idx].date,
                            changefreq, priority)


        # Generate category pages
        for cat in site.categories:
            # When generating pages for In English or In Polish categories,
            # prefer entries in those languages.  This avoids situation where
            # posts available in both languages are confusingly shown in the one
            # preferred by the user (according to their browser configuration)
            # rather than the one corresponding to the category.  There may
            # still be a bit of confusion if user clicks on the entry since then
            # it’ll use their preferred language regardless.
            Post.PREFERRED_LANGUAGE = cat.lang or lang

            entries = sorted(cat.entries, key=lambda p: p.date, reverse=True)
            generate_pages(entries=entries,
                           href=cat.href,
                           filename=cat.filename,
                           title=T(cat))

            filename = os.path.join(os.path.dirname(cat.filename()),
                                    'atom.%s.xml' % lang)
            feed_id = ('http://mina86.com/atom/cat/%s/content/html/' %
                       cat.permalink)
            writer.write_atom(filename, entries, href=cat.href, feed_id=feed_id,
                              title=T(cat))
        Post.PREFERRED_LANGUAGE = lang

        # Link ‘english’ and ‘polish’ to ‘in-$lang’.  I’ve stupidly change the
        # names of the categories and now people who use old paths don’t get any
        # feed.
        writer.link('in-english', 'c/english')
        writer.link('in-polish', 'c/polish')

        # Generate pagination pages (10 entries per page)
        generate_pages(entries=posts,
                       href=lambda page: '/%d' % page if page else '/',
                       filename=lambda lang, page: '%s.%s.html' % (
                           str(page) if page else 'index', lang))

        writer.write_atom('atom.%s.xml' % lang, posts,
                          href='/',
                          feed_id='http://mina86.com/atom/content/html/')

        # Generate posts pages
        for i in range(len(posts)):
            # next and prev are swapped because posts is reversed
            cur = posts[i]
            write_html(cur.filename(lang=lang), 'post', {
                'title': cur.subject,
                'next': posts[i - 1] if i else None,
                'entry': cur,
                'prev': posts[i + 1] if i + 1 < len(posts) else None,
                'canonical': cur.href,
                'archives': archives,
                'categories': categories,
            })
            sitemap_add(cur.url, cur.date, priority='1.0')

        # Generate pages pages
        for entry in site.pages:
            write_html(entry.filename(lang=lang), 'page', {
                'entry': entry,
                'canonical': entry.href,
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
