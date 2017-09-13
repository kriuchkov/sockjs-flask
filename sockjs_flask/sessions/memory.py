from gevent.queue import Queue, Empty
from .. import session

import logging
import gevent

log = logging.getLogger('sockjs_flask')


class MemorySession(session.Session):
    """
    In memory session with a ``gevent.pool.Queue`` as the message store.
    """

    __slots__ = (
        '_queue',
    )

    def __init__(self, *args, **kwargs):
        super(MemorySession, self).__init__(*args, **kwargs)

        self._queue = Queue()

    def add_message(self, frame, data):
        log.info('session closed: %s', self.id)
        self._queue.put_nowait((frame, data))
        #waiter = self._waiter
        #if waiter is not None:
        #    self._waiter = None
        #    if not waiter.cancelled():
        #        waiter.set_result(True)

        self._tick()

    def get_messages(self, timeout=None):
        self._tick()
        messages = []
        # get all messages immediately pending in the queue
        while not self._queue.empty():
            try:
                msg = self._queue.get_nowait()
            except Empty:
                break
            messages.append(msg)

        if not messages:
            try:
                messages.append(self._queue.get(timeout=timeout))
            except Empty:
                pass
        return messages
