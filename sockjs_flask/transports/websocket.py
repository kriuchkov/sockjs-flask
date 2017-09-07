from flask import Flask, Response, request
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from gevent.socket import create_connection

from .base import Transport
from ..exceptions import SessionIsClosed
from ..protocol import STATE_CLOSED, FRAME_CLOSE
from ..protocol import loads, close_frame
from .. import hdrs

import gevent


class EchoApplication(WebSocketApplication):
    def on_open(self):
        print( "Connection opened")

    def on_message(self, message):
        self.ws.send(message)

    def on_close(self, reason):
        print( reason)

class WebSocketTransport(Transport):
    """
    websocket transport
    """

    def server(self, ws, session):
      while True:
        try:
            frame, data = session._wait()
        except SessionIsClosed:
            break
        ws.stream.send_str(data)
        if frame == FRAME_CLOSE:
            try:
                ws.close()
            finally:
                session._remote_closed()

    def client(self, ws, session):
        while True:
            msg = ws.receive()

            if msg.tp == hdrs.WSMsgType.text:
                data = msg.data
                if not data:
                    continue

                if data.startswith('['):
                    data = data[1:-1]

                try:
                    text = loads(data)
                except Exception as exc:
                    session._remote_close(exc)
                    session._remote_closed()
                    ws.close(message=b'broken json')
                    break

                session._remote_message(text)

            elif msg.tp == hdrs.WSMsgType.close:
                session._remote_close()
            elif msg.tp == hdrs.WSMsgType.closed:
                session._remote_closed()
                break

    def process(self):
        pass
        # start websocket connection
        ws = self.ws = Response()
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
        #    #server = gevent.spawn(self.server(ws, self.session))
        #    #client = gevent.spawn(self.client(ws, self.session))
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
        return ws