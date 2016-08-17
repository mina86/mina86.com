import cgi
import os
import sys
import xml.etree.ElementTree as ET

def val(el):
    text = el.text
    return text and text.strip().replace('\r', '').encode('utf-8')


def parse_entry(entry):
    d = {'categories': [], 'comments': []}
    for el in entry:
        if el.tag == 'comment':
            d['comments'].append(parse_comment(el))
        elif el.tag == 'category':
            d['categories'].append(val(el))
        elif el.tag in ('jid', 'level_id', 'comment_mode'):
            pass
        elif el.tag not in ('subject', 'date', 'permalink', 'tags',
                            'trackback', 'body'):
            sys.stderr.write('unexpected tag: entry/%s\n' % el.tag)
        elif el.tag in d:
            sys.stderr.write('duplicate tag: entry/%s\n' % el.tag)
        else:
            d[el.tag] = val(el)

    return d


def parse_comment(comment):
    d = {}
    for el in comment:
        if el.tag not in ('date', 'nick', 'nick_url', 'ip',
                          'trackback', 'body'):
            sys.stderr.write('unexpected tag: entry/comment/%s\n' % el.tag)
        elif el.tag in d:
            sys.stderr.write('duplicate tag: entry/comment/%s\n' % el.tag)
        else:
            d[el.tag] = val(el)
    return d


def write_tag(fd, key, value):
    if value:
        fd.write('<!-- %s: %s -->\n' % (key, value))


def write_comment(fd, d):
    fd.write('\n\n<!-- COMMENT -->\n')
    for key in 'date', 'nick', 'nick_url':
        write_tag(fd, key, d[key])
    fd.write('\n')
    fd.write(d['body'])


def write_entry(fd, d):
    for key in 'subject', 'date', 'tags':
        write_tag(fd, key, d[key])
    write_tag(fd, 'categories', ', '.join(d['categories']))
    fd.write('\n')

    body = d['body'].split('<EXCERPT>', 1)
    summary = None if len(body) < 2 else body[0].strip()
    body = body[-1].strip()

    if summary:
        fd.write(summary)
        fd.write('\n\n<!-- EXCERPT -->\n\n')
    fd.write(body)

    for comment in d['comments']:
        write_comment(fd, comment)


def handle_entry(dirname, el):
    d = parse_entry(el)
    with open(os.path.join(dirname, d['permalink'] + '.html'), 'w') as fd:
        write_entry(fd, d)


def main(argv):
    dirname = 'posts'

    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    first = True
    for el in ET.parse(argv[1]).getroot():
        if el.tag == 'entry':
            handle_entry(dirname, el)
        elif el.tag != 'user' or not first:
            sys.stderr.write('unexpected tag: %s\n' % el.tag)
        first = False


if __name__ == '__main__':
    main(sys.argv)
