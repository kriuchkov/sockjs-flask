from sockjs_flask.session import STATE_NEW
from sockjs_flask import protocol as pt
from gevent.monkey import patch_all
import sockjs_flask
import logging
import gevent

patch_all(thread=False)

logging.basicConfig(
        format='%(asctime)s, %(levelname)-3s [%(filename)s:%(lineno)d][%(module)s:%(funcName)s] - %(message)s',
        datefmt='%H:%M:%S', level=logging.INFO)


def test_session():
    """ Testing sockjs_flask.Session """
    size_ = 4
    s = sockjs_flask.Session( 'test', handler=lambda x, y: print(x, y), debug=True)
    assert s.state == STATE_NEW
    s._acquire()
    for i in range(size_):
        s.send('test_{}'.format(i))
    s._release()
    assert s._queue.qsize() == size_ + 1


def test_acquire_session():
    """ Testing sockjs_flask.Session """
    s = sockjs_flask.Session( 'test', handler=lambda x, y: print(x, y), debug=True)
    assert s.acquired == False
    s._acquire()
    assert s.acquired == True
    s._release()
    assert s.acquired == False


def test_heartbeat_session():
    """ Testing heartbeat from session """
    s = sockjs_flask.Session( 'test', handler=lambda x, y: print(x, y), debug=True)
    s._heartbeat()
    assert s._queue.get_nowait() == (pt.FRAME_HEARTBEAT, pt.FRAME_HEARTBEAT)


def test_waiter_session():
    s = sockjs_flask.Session( 'test', handler=lambda x, y: print(x, y), debug=True)
    s._wait()