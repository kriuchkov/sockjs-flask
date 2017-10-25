# Import kombu modules
from kombu import Consumer, Exchange, Queue, Connection
from kombu.mixins import ConsumerMixin
from kombu.common import maybe_declare
from kombu.pools import producers
from kombu.utils import  reprcall
from kombu.log import get_logger
# Import sockjs_flask modules
from sockjs_flask.protocol import message_frame
from sockjs_flask.database import create_db

import gevent
import weakref


logger = get_logger(__name__)

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

    def raw_channel(self, *args):
        channel = args[0]
        message = args[1]
        for rec in self._hub.database('channel') == channel:
            session = rec['sid']
            session().send_frame(message_frame(message))


class SubscriptionHub(object):

    def __init__(self, manager, connection_string):
        self.database = create_db()
        self._manager = manager
        self._worker = SubscriptionWorker
        self._connection = connection_string

    def _consumer(self):
        """
        Create connection for worker
        :return: void
        """
        try:
            with Connection(self._connection) as conn:
                self._worker(conn, queues, self).run()
        except KeyboardInterrupt:
            print('Bye Bye')

    @staticmethod
    def _send_to_channel(connection, fun, args, kwargs, priority='mid'):
        """
        Send new message to a channel
        :param connection: Connection obj
        :param fun: str
        :param priority: str
        :return: void
        """
        payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
        routing_key = priority_to_routing_key[priority]
        with producers[connection].acquire(block=True) as producer:
            maybe_declare(exchange, producer.channel)
            producer.publish(payload, serializer='pickle', compression='bzip2', exchange=exchange, routing_key=routing_key)

    def _publisher(self, fun, *args, **kwargs):
        """
        Publication new message to a channel
        :param fun: str
        :return: void
        """
        with Connection(self._connection) as conn:
            self._send_to_channel(conn, fun=fun, args=args, kwargs=kwargs, priority='high')
            conn.close()

    def start(self):
        """
        Start consumer worker with gevent
        :return: SubscriptionHub obj
        """
        gevent.spawn(self._consumer)
        return self

    def feed(self, fun, *args, **kwargs):
        """
        Feed queue with gevent
        :param fun: str
        :return: void
        """
        gevent.spawn(self._publisher, fun, *args, **kwargs)

    def subscribe(self, session, channel):
        """
        Subscription from new updates
        :param session: session obj
        :param channel: str
        :return: void
        """
        self.database.insert(sid=weakref.ref(session), channel=channel)

    def unsubscribe(self, session):
        """
        Unsubscription from new updates
        :param session:
        :return: void
        """
        _record = (self.database('sid') == session)
        self.database.delete(_record)


