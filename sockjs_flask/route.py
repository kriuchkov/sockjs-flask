from flask import Response, request
from werkzeug.exceptions import InternalServerError, NotFound, HTTPException

from .session import SessionManager
from .protocol import IFRAME_HTML
from .transports import handlers
from .transports.utils import CACHE_CONTROL
from .transports.utils import session_cookie
from .transports.utils import cors_headers
from .transports.utils import cache_headers
from .transports.rawwebsocket import RawWebSocketTransport
from . import hdrs

import json
import random
import hashlib



def get_manager(name, app):
    return app['__sockjs_managers__'][name]


def _gen_endpoint_name():
    return 'n' + str(random.randint(1000, 9999))


def add_endpoint(app, handler, *, name='', prefix='/sockjs', manager=None, disable_transports=(),
                 sockjs_cdn='https://cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.1.4/sockjs.js', cookie_needed=True):

    assert callable(handler), handler
    router = app.add_url_rule

    if not name:
        name = _gen_endpoint_name()

    if manager is None:
        manager = SessionManager(name, app, handler, debug=app.debug, )

    if manager.name != name:
        raise ValueError('Session manage must have same name as sockjs route')

    # register routes
    route = SockJSRoute(name, manager, sockjs_cdn, handlers, disable_transports, cookie_needed)
    if prefix.endswith('/'):
         prefix = prefix[:-1]
    route_name = 'sockjs-url-%s-greeting' % name
    router(prefix, route_name, view_func=route.greeting)
    # Greeting
    route_name = 'sockjs-url-%s' % name
    router('%s/' % prefix, route_name, view_func=route.greeting, methods=[hdrs.METH_GET, ])
    # Information
    router('%s/info' % prefix, 'sockjs-info-%s' % name, view_func=route.info, methods=[hdrs.METH_GET, ])
    router('%s/info' % prefix, 'sockjs-info-options-%s' % name, view_func=route.info_options, methods=[hdrs.METH_OPTIONS, ])
    # Select transport
    route_name = 'sockjs-%s' % name
    router('%s/<server>/<session>/<transport>' % prefix, route_name, view_func=route.handler, methods=[hdrs.METH_GET, hdrs.METH_POST, hdrs.METH_TRACE ])
    # Sockjs-websocket
    route_name = 'sockjs-websocket-%s' % name
    router('%s/websocket' % prefix, route_name, view_func=route.websocket, methods=[hdrs.METH_GET, ])
    # Sockjs-iframe
    route_name = 'sockjs-iframe-%s' % name
    router('%s/iframe.html' % prefix, route_name, view_func=route.iframe, methods=[hdrs.METH_GET, ])
    # Sockjs-iframe-ver
    route_name = 'sockjs-iframe-ver-%s' % name
    router('%s/iframe{version}.html' % prefix, route_name, view_func=route.iframe, methods=[hdrs.METH_GET, ])
    manager.start()


class SockJSRoute(object):

    def __init__(self, name, manager, sockjs_cdn, handlers, disable_transports, cookie_needed=True):
        self.name = name
        self.manager = manager
        self.handlers = handlers
        self.disable_transports = dict((k, 1) for k in disable_transports)
        self.cookie_needed = cookie_needed
        self.iframe_html = (IFRAME_HTML % sockjs_cdn).encode('utf-8')
        self.iframe_html_hxd = hashlib.md5(self.iframe_html).hexdigest()

    def handler(self, server, session, transport):
        tid = transport

        if tid not in self.handlers or tid in self.disable_transports:
            return NotFound()

        create, transport = self.handlers[tid]
        # session
        manager = self.manager
        if not manager.started:
            manager.start()

        sid = session
        if not sid or '.' in sid or '.' in server:
            return NotFound()

        try:
            session = manager.get(sid, create, request=request)
        except KeyError:
            return NotFound(headers=session_cookie(request))

        t = transport(manager, session, request)
        try:
            return t.process()
        except HTTPException as exc:
            return exc
        except Exception as exc:
            if manager.is_acquired(session):
                manager.release(session)
            return InternalServerError()

    def websocket(self):
        # session
        sid = '%0.9d' % random.randint(1, 2147483647)
        session = self.manager.get(sid, True, request=request)
        transport = RawWebSocketTransport(self.manager, session, request)
        try:
            return (yield from transport.process())
        except HTTPException as exc:
            return exc

    def info(self):
        resp = Response()
        resp.headers[hdrs.CONTENT_TYPE] = 'application/json;charset=UTF-8'
        resp.headers[hdrs.CACHE_CONTROL] = CACHE_CONTROL
        resp.headers.extend(cors_headers(request.headers))

        info = {'entropy': random.randint(1, 2147483647),
                'websocket': 'websocket' not in self.disable_transports,
                'cookie_needed': self.cookie_needed,
                'origins': ['*:*']}
        resp.text = json.dumps(info)
        return resp

    def info_options(self):
        resp = Response(status12=204)
        resp.headers[hdrs.CONTENT_TYPE] = 'application/json;charset=UTF-8'
        resp.headers[hdrs.CACHE_CONTROL] = CACHE_CONTROL
        resp.headers[hdrs.ACCESS_CONTROL_ALLOW_METHODS] = 'OPTIONS, GET'
        resp.headers.extend(cors_headers(request.headers))
        resp.headers.extend(cache_headers())
        resp.headers.extend(session_cookie(request))
        return resp

    def iframe(self):
        cached = request.headers.get(hdrs.IF_NONE_MATCH)
        if cached:
            response = Response(status_code=304)
            response.headers[hdrs.CONTENT_TYPE] = ''
            response.headers.extend(cache_headers())
            return response
        return Response(response=self.iframe_html,
                        headers=((hdrs.CONTENT_TYPE, 'text/html;charset=UTF-8'),
                                 (hdrs.ETAG, self.iframe_html_hxd),) + cache_headers())

    @staticmethod
    def greeting():
        return Response(response=b'Welcome to SockJS!\n',
                        headers=((hdrs.CONTENT_TYPE, 'text/plain; charset=UTF-8'),))