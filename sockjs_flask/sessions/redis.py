from gevent.queue import Queue, Empty
from .. import session

import logging
import gevent
import redis


log = logging.getLogger('sockjs_flask')


class RedisSession(session.Session):
    """ In redis session  """

    __slots__ = (
        'redis_config'
    )

    def __init__(self, *args, **kwargs):
        super(MemorySession, self).__init__(*args, redis_config=None, **kwargs)
        if not redis_config:
            raise Exception('redis_config not found')

        self._queue = redis.StrictRedis(**redis_config)

    def add_message(self, frame, data):
        log.info('session closed: %s', self.id)
        self._queue.put_nowait((frame, data))
        self._queue.set((frame, data))
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