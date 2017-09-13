from ..exceptions import SessionIsAcquired, SessionIsClosed
from ..protocol import close_frame, ENCODING
from ..protocol import STATE_CLOSING, STATE_CLOSED, FRAME_CLOSE, FRAME_MESSAGE

from .. import protocol


class Transport:

    def __init__(self, manager, session, request):
        self.manager = manager
        self.session = session
        self.request = request


class StreamingTransport(Transport):
    """
    Jsonp transport
    """

    timeout = None
    maxsize = 131072

    def __init__(self, manager, session, request):
        super().__init__(manager, session, request)

        self.size = 0
        self.response = None

    def send(self, text):
        blob = (text + '\n').encode(ENCODING)
        self.response.stream.write(blob)

        self.size += len(blob)
        if self.size > self.maxsize:
            return True
        else:
            return False

    def handle_session(self):
        #assert self.response is not None, 'Response is not specified.'

        if self.session.interrupted:
            self.send(close_frame(*protocol.CONN_INTERRUPTED))
        elif self.session.state in (STATE_CLOSING, STATE_CLOSED):
            self.session._remote_closed()
            self.send(close_frame(*protocol.CONN_CLOSED))
        else:
            try:
                self.manager.acquire(self.session)
            except SessionIsAcquired:
                self.send(close_frame(*protocol.CONN_ALREADY_OPEN))
            else:
                try:
                    while True:
                        if self.session.timeout:
                            try:
                                frame, text = self.session._wait()
                            except Exception as e:
                                frame, text = FRAME_MESSAGE, 'a[]'
                        else:
                            frame, text = self.session._wait()

                        if frame == FRAME_CLOSE:
                            self.session._remote_closed()
                            self.send(text)
                            return
                        else:
                            stop = self.send(text)
                            if stop:
                                break
                except Exception as exc:
                    print(exc)
                    self.session._remote_close(exc=exc)
                    self.session._remote_closed()

                except SessionIsClosed as exc:
                    self.session._remote_close(exc=exc)
                    self.session._remote_closed()

                finally:
                    self.manager.release(self.session)