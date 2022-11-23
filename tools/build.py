# Site building script.                            -*- coding: utf-8 -*-
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
import errno
import hashlib
import os
import re
import shutil
import subprocess
import sys

import build_site
import compilers
import paths

SRC_SUBDIR = paths.SRC_SUBDIR
SRC_DATA_SUBDIR = paths.SRC_DATA_SUBDIR
STATIC_SUBDIR = paths.STATIC_SUBDIR
NO_EXPIRY_DIR_NAME = paths.NO_EXPIRY_DIR_NAME

REPO_URL = paths.REPO_URL


def print_action(action, *target):
    print(' %-4s %s' % (action, ' '.join(target)))


class Make(object):
    _make = 'make'

    def __call__(self, targets):
        no_jobserver = not re.search('--jobserver-(?:fds|auth)',
                                     os.environ.get('MAKEFLAGS', ''))
        cmd = [self._make, '-s']
        cmd.extend(targets)
        subprocess.check_call(cmd, close_fds=no_jobserver)

    def set_exe(self, make):
        self._make = make

make = Make()


class Writer(object):

    def __init__(self, out_dir, tmp_dir):
        self._out_dir = out_dir
        self._tmp_dir = tmp_dir
        self._files = []

    tmp_dir = property(lambda self: self._tmp_dir)
    files = property(lambda self: iter(self._files))

    def copy(self, src, *path):
        filename = os.path.join(self._out_dir, *path)
        self._files.append(filename)
        self._cp(src, filename)

    def tmp_copy(self, src, *path):
        self._cp(src, os.path.join(self._tmp_dir, *path), 'CP~')

    def _cp(self, src, dst, action='CP'):
        if isinstance(src, tuple):
            src = os.path.join(*src)

        if (not os.path.isfile(dst) or
            os.path.getmtime(src) > os.path.getmtime(dst)):

            dirname = os.path.dirname(dst)
            try:
                os.makedirs(dirname)
            except OSError as e:
                if e.args[0] != errno.EEXIST:
                    raise

                print_action(action, src, '→', dst)
                shutil.copyfile(src, dst)

    def write_file(self, filename, content, action='GEN'):
        filename = os.path.join(self._out_dir, filename)
        self._files.append(filename)
        if isinstance(content, str):
            content = content.encode('utf-8')

        # If file already exists and has the same content, do not overwrite it
        # so that modification date is not affected.
        if os.path.isfile(filename):
            with open(filename, 'rb') as fd:
                got = fd.read()
                if content == got:
                    return
        else:
            dirname = os.path.dirname(filename)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

        print_action(action, filename)
        with open(filename, 'wb') as fd:
            fd.write(content)

    def link(self, src, dst):
        dst = os.path.join(self._out_dir, dst)
        self._files.append(dst)

        # If link already exists and has the same content, do not overwrite it
        # so we don’t print the action unnecessarily.
        if os.path.exists(dst):
            if os.path.islink(dst):
                got = os.readlink(dst)
                if got == src:
                    return
            os.unlink(dst)
        else:
            dirname = os.path.dirname(dst)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

        print_action('LNK', dst)
        os.symlink(src, dst)


def build_static(writer):
    for dirname, dirnames, filenames in os.walk(STATIC_SUBDIR):
        if dirname == STATIC_SUBDIR:
            dirnames.remove(NO_EXPIRY_DIR_NAME)

        for name in filenames:
            src = os.path.join(dirname, name)
            writer.copy(src, src.split(os.sep, 1)[1])


def build_no_expiry(writer):
    mappings = {}

    def copy(src, content_filter=None):
        content = open(src, 'rb').read()
        if content_filter:
            content = content_filter(content)

        name = hashlib.md5()
        name.update(content)
        name = base64.urlsafe_b64encode(name.digest())[:8].decode('ascii')

        basename = os.path.basename(src)
        basename, ext = os.path.splitext(basename)
        mappings['/d/' + basename] = '/%s/%s' % (NO_EXPIRY_DIR_NAME, name)
        if ext:
            name += ext
            mappings['/d/' + basename + ext ] = '/%s/%s' % (
                NO_EXPIRY_DIR_NAME, name)

        writer.write_file(os.path.join(NO_EXPIRY_DIR_NAME, name), content, 'CP')

    # Copy static/D/* to out/D/* with names changed
    dirname = os.path.join(STATIC_SUBDIR, NO_EXPIRY_DIR_NAME)
    for name in os.listdir(dirname):
        if name[0] != '.':
            copy(os.path.join(dirname, name))

    # Build files from src, put them into .tmp
    paths = []
    for name in os.listdir(SRC_SUBDIR):
        if name[0] == '.':
            continue
        _, ext = os.path.splitext(name)
        if ext in ('.css', '.js', '.less'):
            if ext == '.less':
                name = name[:-4] + 'css'
            paths.append(os.path.join(writer.tmp_dir, name))
    make(paths)

    # Copy files from .tmp to static/D with their new names.
    handlers = {
        '.css': lambda data: compilers.process_css(
            data, SRC_DATA_SUBDIR, mappings).replace(b'/*!', b'/*'),
        '.js': lambda data: b'//%s\n%s' % (REPO_URL.encode('ascii'), data)
    }

    for path in paths:
        copy(path, handlers.get(os.path.splitext(path)[1]))

    return mappings


_IS_COMPRESSABLE_RE = re.compile(
    r'\.(?:%s)$' % '|'.join(('css', 'html', 'js', 'xml', 'gpg', 'svg')))

def is_compressable(path):
    return bool(_IS_COMPRESSABLE_RE.search(path))


def compress(files):
    paths = [path + '.gz' for path in files if is_compressable(path)]
    assert paths
    make(paths)


def cleanup(out_dir, files):
    files = set(files)
    for dirname, _, filenames in os.walk(out_dir):
        for name in filenames:
            path = os.path.join(dirname, name)
            if path.endswith('.gz'):
                uncompressed = path[:-3]
                if (os.path.isfile(uncompressed) and
                    is_compressable(uncompressed) and
                    uncompressed in files):
                    continue
            elif path in files:
                continue
            print_action('RM', path)
            os.unlink(path)


def main(args):
    if args[0].startswith('--make='):
        make.set_exe(args.pop(0)[7:])
    out_dir, = args

    os.chdir(os.path.join(os.path.dirname(__file__), '..'))

    writer = Writer(out_dir, paths.TMP_SUBDIR)

    print_action('...', 'no-expiry files')
    mappings = build_no_expiry(writer)

    print_action('...', 'site')
    build_site.build(writer, mappings)

    print_action('...', 'static files')
    build_static(writer)
    writer.copy((SRC_SUBDIR, 'htaccess', 'main.txt'), '.htaccess')
    writer.copy((SRC_SUBDIR, 'htaccess', 'D.txt'),
                os.path.join(NO_EXPIRY_DIR_NAME, '.htaccess'))

    print_action('...', 'compressed files')
    compress(writer.files)

    print_action('...', 'cleanup')
    cleanup(out_dir, writer.files)

    print(' DONE')


if __name__ == '__main__':
    main(sys.argv[1:])
