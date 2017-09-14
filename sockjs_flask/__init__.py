"""
sockjs-flask - SockJs for Flask
"""
from .session import Session
from .session import SessionManager
from .exceptions import SessionIsClosed
from .exceptions import SessionIsAcquired
from .protocol import STATE_NEW
from .protocol import STATE_OPEN
from .protocol import STATE_CLOSING
from .protocol import STATE_CLOSED
from .protocol import MSG_OPEN
from .protocol import MSG_MESSAGE
from .protocol import MSG_CLOSE
from .protocol import MSG_CLOSED
from .protocol import message_frame
from .route import get_manager, add_endpoint

__version__ = '0.1.9'
__author__ = 'Kryuchkov Nikita <pycodi@hotmail.com>'
__all__ = (
    'get_manager', 'add_endpoint', 'Session', 'SessionManager', 'message_frame',
    'SessionIsClosed', 'SessionIsAcquired', 'STATE_NEW', 'STATE_OPEN', 'STATE_CLOSING', 'STATE_CLOSED', 'MSG_OPEN', 'MSG_MESSAGE', 'MSG_CLOSE', 'MSG_CLOSED',)










