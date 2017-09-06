from flask import Response
from werkzeug.exceptions import Forbidden, InternalServerError

from .. import hdrs
from ..protocol import ENCODING
from .base import StreamingTransport
from .utils import CACHE_CONTROL, session_cookie


class EventsourceTransport(StreamingTransport):
    """
    iframe-eventsource transport
    """

    def send(self, text):
        blob = ''.join(('data: ', text, '\r\n\r\n')).encode(ENCODING)
        self.response.stream.write(blob)
        self.size += len(blob)
        if self.size > self.maxsize:
            return True
        else:
            return False

    def process(self):
        headers = list(((hdrs.CONTENT_TYPE, 'text/event-stream'),
                        (hdrs.CACHE_CONTROL, CACHE_CONTROL)) + session_cookie(self.request))
        # open sequence (sockjs protocol)
        response = self.response = Response(headers=headers, direct_passthrough=True)
        response.stream.write(b'\r\n')
        self.handle_session()
        return response
