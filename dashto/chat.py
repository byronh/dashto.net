import aioredis
import asyncio
import json
import pickle
import signal
import websockets
from pyramid.session import signed_deserialize


class DisconnectError(Exception):
    pass


class NotAuthorizedError(DisconnectError):
    pass


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
            raise NotAuthorizedError('Invalid session token')

        session_data = yield from self.redis.get(session_id)
        session = pickle.loads(session_data)['managed_dict']

        if '_csrft_' not in session or session['_csrft_'] != csrf_token:
            raise NotAuthorizedError('Invalid CSRF token')

        user_id = session.get('user_id')
        if user_id:
            self.user = 'User {}'.format(user_id)
        else:
            self.user = 'Anonymous'
        self.session = session


class ChatServer:
    def __init__(self, listen_host, listen_port, redis_host, redis_port, session_secret):
        self.loop = asyncio.get_event_loop()
        self.host = listen_host
        self.port = listen_port
        self.redis_settings = (redis_host, redis_port)
        self.session_secret = session_secret
        self.clients = []
        self.redis = None
        self.pub = None
        self.sub = None

    def start(self):
        start_server = websockets.serve(self.client_handler, self.host, self.port, klass=Client)

        self.loop.add_signal_handler(signal.SIGINT, asyncio.async, self.on_kill())
        self.loop.add_signal_handler(signal.SIGTERM, asyncio.async, self.on_kill())

        self.loop.run_until_complete(self.connect_to_redis())
        self.loop.run_until_complete(start_server)
        self.loop.run_until_complete(self.publish_handler())

        print('Chat server listening on {}:{}...'.format(self.host, self.port))
        self.loop.run_forever()

    @asyncio.coroutine
    def on_kill(self):
        print('Chat server shutting down...')
        self.loop.stop()

    @asyncio.coroutine
    def connect_to_redis(self):
        self.redis = yield from aioredis.create_redis(self.redis_settings)
        self.pub = yield from aioredis.create_connection(self.redis_settings)
        self.sub = yield from aioredis.create_connection(self.redis_settings)

    @asyncio.coroutine
    def client_handler(self, client, path):
        client.redis = self.redis
        try:
            yield from self.on_connect(client, path)
            while True:
                data = yield from self.receive(client)
                yield from self.pub.execute('publish', 'chan:1', 'Hello!')
                yield from self.broadcast(client.user, data['message'])
        except DisconnectError as e:
            print('Disconnecting {}: {}'.format(client.user, e))
        yield from self.on_disconnect(client)

    @asyncio.coroutine
    def publish_handler(self):
        res = yield from self.sub.execute('subscribe', 'chan:1')
        print(res)
        while True:
            message = yield from self.sub.pubsub_channels['chan:1'].get()
            print('subbed: {}'.format(message))

    @asyncio.coroutine
    def on_connect(self, client, path):
        """ :type client: Client """
        data = yield from self.receive(client)
        if 'cookie' not in data:
            raise NotAuthorizedError('Missing session cookie')
        if 'csrf_token' not in data:
            raise NotAuthorizedError('Missing CSRF token')
        yield from client.authenticate(data['cookie'], data['csrf_token'], self.session_secret)
        print('{} signed in to {}'.format(client.user, path))
        self.clients.append(client)

    @asyncio.coroutine
    def on_disconnect(self, client):
        """ :type client: Client """
        self.clients.remove(client)

    @asyncio.coroutine
    def receive(self, client):
        """ :type client: Client """
        json_data = yield from client.recv()
        if json_data is None:
            raise DisconnectError()
        print('Received {}'.format(json_data))
        try:
            data = json.loads(json_data)
        except (ValueError, TypeError):
            return {}
        return data

    @asyncio.coroutine
    def broadcast(self, user, message):
        print('Broadcasting {}, {}'.format(user, message))
        for client in self.clients:
            yield from client.send('{}: {}'.format(user, message))
