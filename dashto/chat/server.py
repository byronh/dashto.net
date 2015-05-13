import asyncio
import json
import signal
import aioredis
import websockets
from dashto.chat import errors
from dashto.chat.client import Client


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

        print('Chat server listening on {}:{}...'.format(self.host, self.port))

        self.loop.run_until_complete(self.connect_to_redis())
        self.loop.run_until_complete(start_server)
        self.loop.run_until_complete(self.publish_handler())

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
        except errors.DisconnectError as e:
            print('Disconnecting {}: {}'.format(client.user, e))
        yield from self.on_disconnect(client)

    @asyncio.coroutine
    def publish_handler(self):
        res = yield from self.sub.execute('subscribe', 'chan:1')
        if res[2] != 1:
            raise errors.FatalServerError('Failed to subscribe to channel')
        print('Subscribed to channel: {}'.format('chan:1'))
        while True:
            message = yield from self.sub.pubsub_channels['chan:1'].get()
            print('Received message from subscribed channel: {}'.format(message))

    @asyncio.coroutine
    def on_connect(self, client, path):
        """ :type client: dashto.chat.client.Client """
        data = yield from self.receive(client)
        if 'cookie' not in data:
            raise errors.NotAuthorizedError('Missing session cookie')
        if 'csrf_token' not in data:
            raise errors.NotAuthorizedError('Missing CSRF token')
        yield from client.authenticate(data['cookie'], data['csrf_token'], self.session_secret)
        print('{} signed in to {}'.format(client.user, path))
        self.clients.append(client)

    @asyncio.coroutine
    def on_disconnect(self, client):
        """ :type client: dashto.chat.client.Client """
        self.clients.remove(client)

    @asyncio.coroutine
    def receive(self, client):
        """ :type client: dashto.chat.client.Client """
        json_data = yield from client.recv()
        if json_data is None:
            raise errors.DisconnectError('Client closed connection')
        print('Received {}'.format(json_data))
        try:
            data = json.loads(json_data)
        except (ValueError, TypeError):
            return {}
        return data

    @asyncio.coroutine
    def broadcast(self, user, message):
        # TODO send JSON to client
        print('Broadcasting {}, {}'.format(user, message))
        for client in self.clients:
            yield from client.send('{}: {}'.format(user, message))
