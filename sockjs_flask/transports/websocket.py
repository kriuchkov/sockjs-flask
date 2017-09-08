from flask import Response, request
from geventwebsocket.exceptions import WebSocketError


from .base import Transport
from ..exceptions import SessionIsClosed
from ..protocol import STATE_CLOSED, FRAME_CLOSE
from ..protocol import loads, close_frame
from .. import hdrs

import gevent
import logging
import time

log = logging.getLogger('sockjs_flask')


class WebSocketTransport(Transport):
    """
    websocket transport
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
                print(ws)
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
        if request.environ.get('wsgi.websocket'):
            ws = request.environ['wsgi.websocket']
            if self.session.interrupted:
                ws.send(close_frame(1002, 'Connection interrupted'))
            elif self.session.state == STATE_CLOSED:
                ws.send(close_frame(3000, 'Go away!'))
            else:
                try:
                    self.manager.acquire(self.session)
                except:
                   ws.send(close_frame(3000, 'Go away!'))
                   ws.close()
                server = gevent.spawn(self.server, ws, self.session)
                client = gevent.spawn(self.client, ws, self.session)
                gevent.joinall([client, ])
                #try:
                #   gevent.joinall([server, client])
                #except Exception as exc:
                #    self.session._remote_close(exc)
                #finally:
                #    self.manager.release(self.session)
                #    if server.started():
                #        server.kill()
                #    if not client.started():
                #        client.kill()
        return Response(direct_passthrough=True)




            #while True:
            #    message = ws.receive()
            #    ws.send(message)
            #    try:
            #        self.manager.acquire(self.session)
            #    except Exception as e:
            #        print(e)
            #        self.ws.stream.write(close_frame(3000, 'Go away!'))
            #        ws.close()
            #        return ws
                #ws.send(message)
            #return ws
        ## session was interrupted
        #if self.session.interrupted:
        #    self.ws.stream.write(close_frame(1002, 'Connection interrupted'))
        #elif self.session.state == STATE_CLOSED:
        #    self.ws.stream.write(close_frame(3000, 'Go away!'))
###
        #else:
        #    try:
        #        self.manager.acquire(self.session)
        #    except:
        #        self.ws.stream.write(close_frame(3000, 'Go away!'))
        #        ws.close()
        #        return ws
###
        #    #
        #    #
        #    #try:
        #    #    gevent.wait((server, client))
        #    #except Exception as exc:
        #    #    self.session._remote_close(exc)
        #    #finally:
        #    #    self.manager.release(self.session)
        #    #    if not server.done():
        #    #        server.cancel()
            #    if not client.done():
            #        client.cancel()
