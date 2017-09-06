from flask import Response
from werkzeug.exceptions import Forbidden, InternalServerError

from .. import hdrs
from ..protocol import dumps, ENCODING
from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie, cors_headers

import asyncio
import re


PRELUDE1 = b"""
<!doctype html>
<html><head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
</head><body><h2>Don't panic!</h2>
  <script>
    document.domain = document.domain;
    var c = parent."""

PRELUDE2 = b""";
    c.start();
    function p(d) {c.message(d);};
    window.onload = function() {c.stop();};
  </script>"""


class HTMLFileTransport(StreamingTransport):
    """
    iframe-htmlfile transport
    """

    maxsize = 131072
    check_callback = re.compile('^[a-zA-Z0-9_\.]+$')

    def send(self, text):
        blob = ('<script>\np(%s);\n</script>\r\n' % dumps(text)).encode(ENCODING)
        self.response.write(blob)
        self.size += len(blob)
        if self.size > self.maxsize:
            return True
        else:
            return False

    def process(self):
        request = self.request

        print(dir(request))
        callback = request.args.get('c', None)

        if callback is None:
           self.session._remote_closed()
           return InternalServerError(description='"callback" parameter required')

       #elif not self.check_callback.match(callback):
       #    yield from self.session._remote_closed()
       #    return InternalServerError(body=b'invalid "callback" parameter')

        headers = list(((hdrs.CONTENT_TYPE, 'text/html; charset=UTF-8'), (hdrs.CACHE_CONTROL, CACHE_CONTROL),
                       (hdrs.CONNECTION, 'close')) + session_cookie(request) + cors_headers(request.headers))

        resp = self.response = Response(direct_passthrough=True, headers=headers)
        #yield from resp.prepare(self.request)
        print(callback)
        resp.stream.write(b''.join((PRELUDE1, callback.encode('utf-8'), PRELUDE2, b' '*1024)))

        #yield from self.handle_session()
        return resp