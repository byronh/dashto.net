#!/usr/bin/env python

import argparse
import getpass
import transaction
from dashto.models import Base, DBSession
from dashto.models import User
from pyramid.paster import bootstrap
from sqlalchemy import engine_from_config


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', required=True, help='.ini configuration file to load settings from')
    args = parser.parse_args()

    env = bootstrap(args.config)
    settings = env['registry'].settings

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    print('Creating new user...')

    user = User()
    user.name = input('Username: ')
    user.password = getpass.getpass('Password: ')

    DBSession.add(user)
    transaction.commit()

    print('User successfully created!')
