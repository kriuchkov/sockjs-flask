from flask import Response, request
from geventwebsocket.exceptions import WebSocketError

from .base import Transport
from ..exceptions import SessionIsClosed
from ..protocol import STATE_CLOSED, FRAME_CLOSE
from ..protocol import loads, close_frame
from .. import protocol

import gevent
import logging


log = logging.getLogger('sockjs_flask')


class WebSocketTransport(Transport):
    """
    Websocket transport
    """
    def server(self, ws, session):
        log.info('started websocket server: %s', self.session.id)
        while True:
            try:
                log.info('frame for websocket server: %s', self.session.id)
                frame, data = session._wait()
                ws.send(data)
            except SessionIsClosed:
                log.info('Break for websocket server: %s', self.session.id)
                break
            except WebSocketError as e:
                break
            if frame == FRAME_CLOSE:
                log.warning('closed websocket server: %s', self.session.id)
                try:
                    ws.close()
                finally:
                    session._remote_closed()

    def client(self, ws, session):
        log.info('started websocket client: %s', self.session.id)
        while True:
            log.info('frame for websocket client: {} whit session closed {}'.format(self.session.id, ws.closed))
            if not ws.closed:
                data = ws.receive()
                if not data:
                    continue

                if data.startswith('['):
                    data = data[1:-1]

                try:
                    text = loads(data)
                except Exception as exc:
                    session._remote_close(exc)
                    session._remote_closed()
                    ws.close(message='broken json')
                    break

                session._remote_message(text)
            else:
                session._remote_close()
                session._remote_closed()
                break

    def process(self):
        log.info('1. Run process for websocket with session: %s', self.session.id)
        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            if self.session.interrupted:
                ws.send(close_frame(*protocol.CONN_INTERRUPTED))
            elif self.session.state == STATE_CLOSED:
                ws.send(close_frame(*protocol.CONN_CLOSED))
            else:
                try:
                    log.info('1.1. websocket acquire session: %s', self.session.id)
                    self.manager.acquire(self.session)
                except:
                    log.info('1.2. websocket CONN_CLOSED: %s', self.session.id)
                    ws.send(close_frame(*protocol.CONN_CLOSED))
                    ws.close()
                log.info('1.3 Run client and server for websocket: %s', self.session.id)
                server = gevent.spawn(self.server, ws, self.session)
                client = gevent.spawn(self.client, ws, self.session)
                try:
                    log.info('1.4. Gevent waiter : %s', self.session.id)
                    gevent.joinall([server, client])
                except Exception as exc:
                    self.session._remote_close(exc)
                finally:
                    log.info('1.5. Finally for process websocket: %s', self.session.id)
                    self.manager.release(self.session)
                    if server.started:
                        log.info('1.6. Stop server with session: %s', self.session.id)
                        server.kill()
                    if client.started:
                        log.info('1.7. Stop client with session: %s', self.session.id)
                        client.kill()
        return Response(direct_passthrough=True)