from gevent.queue import Queue, Empty
from .. import session

import logging
import gevent

log = logging.getLogger('sockjs_flask')


class ZeroSession(session.Session):
    pass