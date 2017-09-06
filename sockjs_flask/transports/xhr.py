from flask import Response

from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie, cors_headers, cache_headers
from .. import hdrs


class XHRTransport(StreamingTransport):
    """
    Long polling derivative transports,
    used for XHRPolling and JSONPolling.
    """

    maxsize = 0

    def process(self):
        request = self.request

        if request.method == hdrs.METH_OPTIONS:
            headers = list(((hdrs.CONTENT_TYPE, 'application/javascript; charset=UTF-8'),
                           (hdrs.ACCESS_CONTROL_ALLOW_METHODS, 'OPTIONS, POST')) +
                           session_cookie(request) + cors_headers(request.headers) + cache_headers())
            return Response(status_code=204, headers=headers)

        headers = list(((hdrs.CONTENT_TYPE, 'application/javascript; charset=UTF-8'),
                       (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(request) + cors_headers(request.headers))

        response = self.response = Response(headers=headers)
        self.handle_session()
        return response
