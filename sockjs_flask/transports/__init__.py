from .jsonp import JSONPolling
from .websocket import WebSocketTransport
from .ihf import HTMLFileTransport
from .eventsource import EventsourceTransport
from .xhr import XHRTransport
from .xhrsend import XHRSendTransport
from .xhrstreaming import XHRStreamingTransport


handlers = {
     # 'websocket': (True, WebSocketTransport),
      'xhr': (True, XHRTransport),
      'xhr_send': (True, XHRSendTransport),
     # 'xhr_streaming': (True, XHRStreamingTransport),
    #  'jsonp': (True, JSONPolling),
    #  'jsonp_send': (False, JSONPolling),
    #  'htmlfile': (True, HTMLFileTransport),
     # 'eventsource': (True, EventsourceTransport),
}