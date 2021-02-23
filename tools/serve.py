import http.server
import os
import ssl
import sys
import subprocess
import typing


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = http.server.SimpleHTTPRequestHandler.extensions_map
    extensions_map.setdefault('.webp', 'image/webp')

    def __init__(self, *args: typing.Any, **kw: typing.Any):
        directory = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                  '../public/mina86.com'))
        try:
            super().__init__(*args, directory=directory, **kw)
        except ConnectionResetError:
            pass

    def translate_path(self, path: str) -> str:
         path = super().translate_path(path)
         if not os.path.exists(path):
             for lang in ('.', '.en.'):
                 for ext in ('html', 'png', 'jpg', 'svg', 'css', 'js', 'xml'):
                     p = path + lang + ext
                     if os.path.exists(p):
                         return p
         elif os.path.isdir(path):
             for name in ('index.html', 'index.en.html'):
                 p = os.path.join(path, name)
                 if os.path.exists(p):
                     return p
         return path


def get_certfile() -> str:
    certfile = os.path.realpath(os.path.join(
        os.path.dirname(__file__), os.pardir, '.tmp', 'serve.pem'))
    if not os.path.isfile(certfile):
        subprocess.run(('openssl', 'req', '-new', '-x509', '-keyout', certfile,
                        '-out', certfile, '-days', '3650', '-nodes', '-batch',
                        '-verbose'),
                       cwd='/')
    return certfile

def main():
    port = 4443
    httpd = http.server.HTTPServer(('0.0.0.0', port), Handler)
    httpd.socket = ssl.wrap_socket(
        httpd.socket, server_side=True, certfile=get_certfile())
    print('https://127.0.0.1:{}/'.format(port))
    httpd.serve_forever()

if __name__ == '__main__':
    main()
