import asyncio
import json
import logging
import signal
import aioredis
import websockets
from dashto.chat import errors
from dashto.chat.channel import Channel
from dashto.chat.client import Client


class ChatServer:
    def __init__(self, listen_host, listen_port, redis_host, redis_port, session_secret):
        self.logger = logging.getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.host = listen_host
        self.port = listen_port
        self.redis_settings = (redis_host, redis_port)
        self.session_secret = session_secret
        self.clients = []
        self.redis = None
        self.pub = None
        self.sub = None

        self.channels = {}

    def start(self):
        try:
            start_server = websockets.serve(self.client_handler, self.host, self.port, klass=Client)

            self.loop.add_signal_handler(signal.SIGINT, asyncio.async, self.on_kill())
            self.loop.add_signal_handler(signal.SIGTERM, asyncio.async, self.on_kill())

            print('campaign server listening on {}:{}...'.format(self.host, self.port))

            self.loop.run_until_complete(self.connect_to_redis())
            self.loop.run_until_complete(start_server)
            self.loop.run_until_complete(self.publish_handler())

            self.loop.run_forever()
        except Exception as e:
            self.logger.exception(e)

    @asyncio.coroutine
    def on_kill(self):
        print('campaign server shutting down...')
        self.loop.stop()

    @asyncio.coroutine
    def connect_to_redis(self):
        self.redis = yield from aioredis.create_redis(self.redis_settings)
        self.pub = yield from aioredis.create_redis(self.redis_settings)
        self.sub = yield from aioredis.create_redis(self.redis_settings)

    @asyncio.coroutine
    def client_handler(self, client, path):
        client.redis = self.redis
        campaign_id = None
        try:
            campaign_id = yield from self.connect_to_channel(client, path)
            if campaign_id not in self.channels:
                channel = Channel(self.redis, self.sub, 'campaign:{}'.format(campaign_id))
                self.channels[campaign_id] = channel
            else:
                channel = self.channels[campaign_id]
            yield from channel.add_client(client)
            while True:
                data = yield from self.receive(client)
                yield from channel.publish_json(data)
        except errors.DisconnectError as e:
            print('user:{} -> {}'.format(client.user, e))
        finally:
            if campaign_id is not None:
                yield from self.channels[campaign_id].remove_client(client)
            self.clients.remove(client)

    @asyncio.coroutine
    def publish_handler(self):
        while True:
            for channel_id, channel in self.channels.items():
                # TODO yield from constructor in channel object so that this doesn't need to be checked
                if not channel.channel:
                    continue
                data = yield from channel.get_json()
                if not data:
                    continue
                yield from channel.broadcast(data)
            yield from asyncio.sleep(0.01)

    @asyncio.coroutine
    def connect_to_channel(self, client, path):
        """ :type client: dashto.chat.client.Client """
        data = yield from self.receive(client)
        if 'channel_id' not in data:
            raise errors.NotAuthorizedError('missing channel specifier')
        try:
            channel_id = int(data['channel_id'])
        except TypeError:
            raise errors.NotAuthorizedError('invalid channel specifier')
        if 'cookie' not in data:
            raise errors.NotAuthorizedError('missing session cookie')
        if 'csrf_token' not in data:
            raise errors.NotAuthorizedError('missing CSRF token')
        yield from client.authenticate(data['cookie'], data['csrf_token'], self.session_secret)
        self.clients.append(client)
        return channel_id

    @asyncio.coroutine
    def receive(self, client):
        """ :type client: dashto.chat.client.Client """
        json_data = yield from client.recv()
        if json_data is None:
            raise errors.DisconnectError('client closed connection')
        try:
            data = json.loads(json_data)
        except (ValueError, TypeError):
            return {}
        return data
