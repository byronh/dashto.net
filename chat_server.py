import asyncio
import websockets

clients = []


@asyncio.coroutine
def chat_handler(websocket, path):
    print('Client connected')
    clients.append(websocket)
    while True:
        message = yield from websocket.recv()
        if message is None:
            break
        if len(message) == 0:
            continue
        print('Client sent: {}'.format(message))
        for client in clients:
            user_num = clients.index(websocket) + 1
            yield from client.send('User {}: {}'.format(user_num, message))
    print('Client disconnected')
    clients.remove(websocket)


if __name__ == '__main__':
    host, port = '0.0.0.0', 5001
    start_server = websockets.serve(chat_handler, host, port)
    print('Chat server listening on {}:{}...'.format(host, port))

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
