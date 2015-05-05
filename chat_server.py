#!/usr/bin/env python

import argparse
from pyramid.paster import bootstrap
from dashto.chat import ChatServer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help='.ini configuration file to load settings from')
    args = parser.parse_args()

    env = bootstrap(args.config)
    settings = env['registry'].settings

    chat_server = ChatServer(
        listen_host=settings['chat.listen_host'],
        listen_port=settings['chat.listen_port'],
        redis_host=settings['redis.sessions.host'],
        redis_port=settings['redis.sessions.port'],
        session_secret=settings['redis.sessions.secret']
    )
    chat_server.start()
