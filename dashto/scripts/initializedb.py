import os
import sqlalchemy
import sys
import transaction
from dashto.db import DBSession, Base
from dashto.models import User
from pyramid import paster


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    paster.setup_logging(config_uri)
    settings = paster.get_appsettings(config_uri)

    engine = sqlalchemy.engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        model = User(name='admin', email='admin@dashto.net', password='admin')
        DBSession.add(model)
