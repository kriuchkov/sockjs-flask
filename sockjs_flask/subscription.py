from kombu import Consumer, Exchange, Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.common import maybe_declare
from kombu.pools import producers
from kombu.utils import  reprcall
from kombu.log import get_logger

from .protocol import message_frame
from .database import create_db


import gevent
import datetime
import time
import weakref


logger = get_logger(__name__)


connection_string = 'amqp://guest@localhost//'


exchange = Exchange('subscription1', type='direct', auto_delet=True, delivery_mode=1)
priority_to_routing_key = {'high': 'hipri', 'mid': 'midpri', 'low': 'lopri'}

queues =[
    Queue('hipri', exchange, routing_key='hipri'),
    Queue('midpri', exchange, routing_key='midpri'),
    Queue('lopri', exchange, routing_key='lopri')
]


class SubscriptionWorker(ConsumerMixin):

    def __init__(self, connection, queues, hub):

        self.connection = connection
        self.queues = queues
        self._hub = hub

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues, callbacks=[self.process_task,], accept=['pickle',])]

    def process_task(self, body, message):
        fun = body['fun']
        args = body['args']
        kwargs = body['kwargs']
        logger.info('Got task: %s', reprcall(fun, args, kwargs))
        try:
            fun = getattr(self, fun)
            fun(*args, **kwargs)
        except Exception as exc:
            logger.error('task raised exception: %r', exc)
        message.ack()

    def send_db(self, *args):
        channel = args[0]
        message = args[1]
        for rec in self._hub.database('channel') == channel:
            session = rec['sid']
            session().send_frame(message_frame(message))


class SubscriptionHub(object):

    def __init__(self, manager):
        self.database = create_db()
        self._manager = manager
        self._worker = SubscriptionWorker

    def _consumer(self):
        try:
            with Connection(connection_string) as conn:
                self._worker(conn, queues, self).run()
        except KeyboardInterrupt:
            print('bye bye')

    def _publisher(self, channel, msg):
        with Connection(connection_string) as conn:
            self._send_to_channel(conn, fun='send_db', args=(channel, msg), kwargs={}, priority='high')
            conn.close()

    @staticmethod
    def _send_to_channel(connection, fun, args=(), kwargs={}, priority='mid'):
        payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
        routing_key = priority_to_routing_key[priority]
        with producers[connection].acquire(block=True) as producer:
            maybe_declare(exchange, producer.channel)
            producer.publish(payload, serializer='pickle', compression='bzip2', exchange=exchange, routing_key=routing_key)

    def start(self):
        gevent.spawn(self._consumer)
        return self

    def feed(self, channel, msg):
        gevent.spawn(self._publisher, channel, msg)

    def subscribe(self, session, channel):
        self.database.insert(sid=weakref.ref(session), channel=channel)
        #gevent.spawn(self._publisher, channel, '32')



