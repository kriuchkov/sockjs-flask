from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import Forbidden, InternalServerError

from ..protocol import loads, ENCODING
from .base import Transport
from .utils import CACHE_CONTROL, session_cookie, cors_headers, cache_headers
from .. import hdrs


class XHRSendTransport(Transport):

    def process(self):
        request = self.request

        if request.method not in (hdrs.METH_GET, hdrs.METH_POST, hdrs.METH_OPTIONS):
            return Forbidden(text='Method is not allowed')

        cors_ = cors_headers(request.headers, self.manager.debug)

        if self.request.method == hdrs.METH_OPTIONS:
            base_headers = ((hdrs.ACCESS_CONTROL_ALLOW_METHODS, 'OPTIONS, POST'),
                            (hdrs.CONTENT_TYPE, 'application/javascript; charset=UTF-8'))
            headers = list(base_headers + session_cookie(request) + cors_ + cache_headers())
            return Response(status_code=204, headers=headers)

        data = request.data
        if not data:
            return InternalServerError(text='Payload expected.')
        try:
            messages = loads(data.decode(ENCODING))
        except:
            return InternalServerError(text="Broken JSON encoding.")

        self.session._remote_message(messages)
        headers = list(((hdrs.CONTENT_TYPE, 'text/plain; charset=UTF-8'),
                        (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(request) + cors_)
        return Response(status=204, headers=headers)