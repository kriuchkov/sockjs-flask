from gevent import pywsgi
from .handler import Handler


class Server(pywsgi.WSGIServer):
    """
    """

    application = None

    def __init__(self, listener, *args,  **kwargs):
        kwargs.setdefault('handler_class', Handler)
        pywsgi.WSGIServer.__init__(self, listener, *args, **kwargs)
