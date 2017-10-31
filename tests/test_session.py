import sockjs_flask
import logging

logging.basicConfig(level=logging.INFO)


__name = 'test'


def handler(msg, session):
    print(msg)
    print(session)


def test_session():
    """ Testing sockjs_flask.Session """
    size_ = 4
    s = sockjs_flask.Session(__name, handler=handler, debug=True)
    s._acquire()
    for i in range(size_):
        s.send('test_{}'.format(i))
    s._release()
    assert s._queue.qsize() == size_ + 1


def test_session_acquire():
    """ Testing sockjs_flask.Session """
    size_ = 4
    s = sockjs_flask.Session(__name, handler=handler, debug=True)
    s._acquire()
    print(s.is_acquired(s))