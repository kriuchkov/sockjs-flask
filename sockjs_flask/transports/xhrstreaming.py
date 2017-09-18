from flask import Response, request
from flask import stream_with_context

from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie, cors_headers, cache_headers
from .. import hdrs

import gevent
import logging
import time

log = logging.getLogger('sockjs_flask')


def gen():
    yield b'o'
    time.sleep(20)
    time.sleep(2)


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
        response = self.response = Response(headers=headers)
        response.stream.write(self.open_seq)
        handle_session = gevent.spawn(self.handle_session)
        ##yield stream_with_context(response)
        handle_session.join()
        response.close()
        return response
