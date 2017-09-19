from sockjs_flask.handler import Handler
from gunicorn.workers.ggevent import GeventPyWSGIWorker


class GeventWebSocketWorker(GeventPyWSGIWorker):
    wsgi_handler = Handler