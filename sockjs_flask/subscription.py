from kombu import Consumer, Exchange, Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.common import maybe_declare
from kombu.pools import producers
from kombu.utils import  reprcall
from kombu.log import get_logger


from .database import create_db


import gevent
import datetime
import time

logger = get_logger(__name__)


connection_string = 'amqp://guest@localhost//'


exchange = Exchange('subscription1', type='direct', auto_delet=True, delivery_mode=1)

priority_to_routing_key = {'high': 'hipri',
                           'mid': 'midpri',
                           'low': 'lopri'}

queues =[
    Queue('hipri', exchange, routing_key='hipri'),
    Queue('midpri', exchange, routing_key='midpri'),
    Queue('lopri', exchange, routing_key='lopri')
]


class SubscriptionWorker(ConsumerMixin):

    def __init__(self, connection, queues):
        self.connection = connection
        self.queues = queues

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=self.queues, callbacks=[self.process_task,], accept=['pickle',])]

    def process_task(self, body, message):
        fun = body['fun']
        args = body['args']
        kwargs = body['kwargs']
        logger.info('Got task: %s', reprcall(fun.__name__, args, kwargs))
        try:
            fun(*args, **kwargs)
        except Exception as exc:
            logger.error('task raised exception: %r', exc)
        message.ack()

    @staticmethod
    def send_frame(msg):
        print("Hello %s" % (msg,))


class SubscriptionHub(object):

    def __init__(self, manager):
        self._manager = manager
        self._worker = SubscriptionWorker
        self.database = create_db()

    def _consumer(self):
        try:
            with Connection(connection_string) as conn:
                self._worker(conn, queues).run()
        except KeyboardInterrupt:
            print('bye bye')

    def _publisher(self, msg):
        with Connection(connection_string) as conn:
            self._send_to_channel(conn, fun=self._worker.send_frame, args=(msg, ), kwargs={}, priority='high')
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

    def feed(self, msg):
        gevent.spawn(self._publisher, msg)

