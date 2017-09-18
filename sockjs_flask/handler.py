from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

__all__ = [
    'Handler'
]


class HandlerStream(object):

    __slots__ = ('handler', 'read', 'write')

    def __init__(self, handler):
        self.handler = handler

        socket = handler.socket
        rfile = handler.rfile

        if not rfile:
            rfile = socket.makefile('rb', -1)

        self.read = rfile.read
        self.write = socket.sendall


class Handler(WebSocketHandler):

    stream = None

    def run_application(self):
        self.stream = self.make_stream()
        super().run_application()

    def make_stream(self):
        return HandlerStream(self)