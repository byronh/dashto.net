import pickle
import websockets
from dashto.chat import errors
from pyramid.session import signed_deserialize


class Client(websockets.WebSocketServerProtocol):
    def __init__(self, ws_handler, *, origins=None, subprotocols=None, **kwds):
        super().__init__(ws_handler, origins=origins, subprotocols=subprotocols, **kwds)
        self.user = None
        self.redis = None
        self.session = None

    def authenticate(self, cookie, csrf_token, session_secret):
        session_id = cookie.replace('session=', '')
        try:
            session_id = signed_deserialize(session_id, session_secret)
        except ValueError:
            raise errors.NotAuthorizedError('Invalid session token')

        session_data = yield from self.redis.get(session_id)
        session = pickle.loads(session_data)['managed_dict']

        if session['_csrft_'] != csrf_token:
            raise errors.NotAuthorizedError('Invalid CSRF token')

        user_id = session.get('user_id')
        if user_id:
            self.user = 'User {}'.format(user_id)
        else:
            self.user = 'Anonymous'
        self.session = session
