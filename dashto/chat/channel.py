import asyncio
import json
from aioredis.errors import ChannelClosedError
from dashto.chat import errors


class Channel:
    def __init__(self, pub_client, sub_client, name):
        self.channel = None
        self.clients = []
        self.loop = asyncio.get_event_loop()
        self.name = name
        self.pub = pub_client
        self.sub = sub_client

    @asyncio.coroutine
    def subscribe(self):
        res = yield from self.sub.subscribe(self.name)
        if len(res) != 1:
            raise errors.FatalServerError('Failed to subscribe to channel {}'.format(self.name))
        self.channel = res[0]
        print('{} -> [opened]'.format(self.name))

    @asyncio.coroutine
    def unsubscribe(self):
        yield from self.sub.unsubscribe(self.name)
        print('{} -> [closed]'.format(self.name))

    @asyncio.coroutine
    def add_client(self, client):
        if not self.clients:
            yield from self.subscribe()
        self.clients.append(client)

    @asyncio.coroutine
    def remove_client(self, client):
        self.clients.remove(client)
        if not self.clients:
            yield from self.unsubscribe()

    @asyncio.coroutine
    def get_json(self):
        try:
            data = yield from self.channel.get_json()
            print('{} -> received {}'.format(self.name, data))
            return data
        except ValueError:
            print('{} -> ignoring invalid json'.format(self.name))
            return None
        except ChannelClosedError:
            return None

    @asyncio.coroutine
    def publish_json(self, data):
        yield from self.pub.publish_json(self.name, json.dumps(data))

    @asyncio.coroutine
    def broadcast(self, data):
        print('{} -> broadcasting {}'.format(self.name, data))
        for client in self.clients:
            yield from client.send(json.dumps(data))
