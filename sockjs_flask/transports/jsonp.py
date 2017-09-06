from flask import Response
from werkzeug.exceptions import Forbidden, InternalServerError, BadRequest
from urllib.parse import unquote_plus


from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie, cors_headers
from ..protocol import dumps, loads, ENCODING
from .. import hdrs

import re


class JSONPolling(StreamingTransport):
    """
    jsonp transport
    """

    check_callback = re.compile('^[a-zA-Z0-9_\.]+$')
    callback = ''

    def send(self, text):
        data = '/**/%s(%s);\r\n' % (self.callback, dumps(text))
        self.response.stream.write(data.encode(ENCODING))
        return True

    def process(self):
        session = self.session
        request = self.request
        meth = request.method

        if request.method == hdrs.METH_GET:
            callback = request.args.get('c', None)

            if not callback:
                self.session._remote_closed()
                return InternalServerError(description='"callback" parameter required')

            elif not self.check_callback.match(callback):
                self.session._remote_closed()
                return InternalServerError(description='invalid "callback" parameter')

            headers = list(((hdrs.CONTENT_TYPE, 'application/javascript; charset=UTF-8'),
                            (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(request) + cors_headers(request.headers))

            resp = self.response = Response(headers=headers)
            #yield from resp.prepare(request)
            self.handle_session()
            return resp

        elif request.method == hdrs.METH_POST:
            data = request.data

            ctype = request.content_type.lower()
            if ctype == 'application/x-www-form-urlencoded':
                if not data.startswith(b'd='):
                    return InternalServerError(description='Payload expected.')
                data = unquote_plus(data[2:].decode(ENCODING))
            else:
                data = data.decode(ENCODING)

            if not data:
                return InternalServerError(description='Payload expected.')
            try:
                messages = loads(data)
            except:
                return InternalServerError(description='Broken JSON encoding.')

            #yield from session._remote_messages(messages)
            return Response(response='ok', headers=((hdrs.CONTENT_TYPE, 'text/plain; charset=UTF-8'),
                                                    (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(request))

        else:
            return BadRequest(description="No support for such method: %s" % meth)