import asyncio
import asyncio_redis
# import pickle
import json
import websockets
# from asyncio_redis.encoders import BaseEncoder, BytesEncoder
from pyramid.session import signed_deserialize


# class PickleEncoder(BaseEncoder):
#     native_type = str
#
#     def encode_from_native(self, data):
#         return pickle.loads(data.encode('utf-8'))
#
#     def decode_to_native(self, data):
#         return pickle.dumps(data)


class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.redis = None

    def start(self):
        start_server = websockets.serve(self.client_handler, self.host, self.port)
        print('Chat server listening on {}:{}...'.format(self.host, self.port))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_server)
        loop.run_until_complete(self.connect_to_redis())
        loop.run_forever()

    @asyncio.coroutine
    def connect_to_redis(self):
        self.redis = yield from asyncio_redis.Connection.create(
            host='localhost',
            port=6379,
            # encoder=PickleEncoder()
        )

    @asyncio.coroutine
    def client_handler(self, websocket, path):
        yield from self.on_connect(websocket, path)

        while True:
            json_data = yield from websocket.recv()
            if json_data is None:
                break
            if len(json_data) == 0:
                continue
            data = json.loads(json_data)
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
        session_id = signed_deserialize(session_id, 'insecure_secret')

        # session_data = yield from self.redis.get(session_id)
        # print(session_data)
        # print(type(session_data))
        yield from self.broadcast(data['message'])

    @asyncio.coroutine
    def broadcast(self, message):
        for client in self.clients:
            # user_num = self.clients.index(websocket) + 1
            yield from client.send('User {}: {}'.format(0, message))

if __name__ == '__main__':
    chat_server = ChatServer('0.0.0.0', 5001)
    chat_server.start()
