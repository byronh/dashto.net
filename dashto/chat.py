import aioredis
import asyncio
import json
import pickle
import signal
import websockets
from pyramid.session import signed_deserialize


class ChatServer:
    def __init__(self, listen_host, listen_port, redis_host, redis_port, session_secret):
        self.loop = asyncio.get_event_loop()
        self.host = listen_host
        self.port = listen_port
        self.redis_settings = (redis_host, redis_port)
        self.session_secret = session_secret
        self.clients = []
        self.redis = None

    def start(self):
        start_server = websockets.serve(self.client_handler, self.host, self.port)

        self.loop.add_signal_handler(signal.SIGINT, asyncio.async, self.on_kill())
        self.loop.add_signal_handler(signal.SIGTERM, asyncio.async, self.on_kill())

        self.loop.run_until_complete(self.connect_to_redis())
        self.loop.run_until_complete(start_server)

        print('Chat server listening on {}:{}...'.format(self.host, self.port))
        self.loop.run_forever()

    @asyncio.coroutine
    def on_kill(self):
        print('Chat server shutting down...')
        self.loop.stop()

    @asyncio.coroutine
    def connect_to_redis(self):
        self.redis = yield from aioredis.create_redis(self.redis_settings)

    @asyncio.coroutine
    def client_handler(self, websocket, path):
        yield from self.on_connect(websocket, path)

        while True:
            json_data = yield from websocket.recv()
            try:
                data = json.loads(json_data)
            except (ValueError, TypeError):
                break
            yield from self.on_receive(websocket, data)

        yield from self.on_disconnect(websocket)

    @asyncio.coroutine
    def on_connect(self, websocket, path):
        print('Client connected to {}'.format(path))
        self.clients.append(websocket)

    @asyncio.coroutine
    def on_disconnect(self, websocket):
        print('Client disconnected')
        self.clients.remove(websocket)

    @asyncio.coroutine
    def on_receive(self, websocket, data):
        session_id = data['cookie'].replace('session=', '')
        session_id = signed_deserialize(session_id, self.session_secret)

        session_data = yield from self.redis.get(session_id)
        session = pickle.loads(session_data)
        user_id = session['managed_dict'].get('user_id')
        if user_id:
            user = 'User {}'.format(user_id)
        else:
            user = 'Anonymous'
        yield from self.broadcast(user, data['message'])

    @asyncio.coroutine
    def broadcast(self, user, message):
        for client in self.clients:
            yield from client.send('{}: {}'.format(user, message))
