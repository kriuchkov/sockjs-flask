from flask import Response, request
from flask import stream_with_context

from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie, cors_headers, cache_headers
from .. import hdrs

import gevent
import logging

log = logging.getLogger('sockjs_flask')


class XHRStreamingTransport(StreamingTransport):

    maxsize = 131072
    open_seq = b'h' * 2048 + b'\n'

    def process(self):
        request = self.request

        headers = list(((hdrs.CONNECTION, request.headers.get(hdrs.CONNECTION, 'close')),
                        (hdrs.CONTENT_TYPE,'application/javascript; charset=UTF-8'),
                        (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(request) + cors_headers(request.headers))

        if request.method == hdrs.METH_OPTIONS:
            headers.append((hdrs.ACCESS_CONTROL_ALLOW_METHODS, 'OPTIONS, POST'))
            headers.extend(cache_headers())
            return Response(status=204, headers=headers)
        # open sequence (sockjs protocol)
        #response = request.environ.get('wsgi.websocket')
        #_ws = request.steam
        response = self.response = Response(headers=headers, direct_passthrough=True)
        response.stream.write(self.open_seq)
        handle_session = gevent.spawn(self.handle_session)
        #response.close()
        yield stream_with_context(response)
        handle_session.join()
