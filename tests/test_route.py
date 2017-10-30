from werkzeug.test import Client
from werkzeug.testapp import test_app

import sockjs_flask


def test_sockjs_route_info():
    sockjs_route = sockjs_flask.SockJSRoute(
        'test', '', 'https://cdnjs.cloudflare.com/ajax/libs/sockjs-client/1.1.4/sockjs.js', (), (), debug=True)
    assert type(sockjs_route.info()) == dict
