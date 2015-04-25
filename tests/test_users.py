import unittest
import sqlalchemy
import transaction
from dashto.db import DBSession, Base
from dashto.models import User
from dashto.views import Controller
from pyramid import testing


class TestSuccess(unittest.TestCase):
    def setup_method(self, method):
        self.config = testing.setUp()
        engine = sqlalchemy.create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        with transaction.manager:
            model = User(name='admin', email='admin@example.com', password='1234')
            DBSession.add(model)

    def teardown_method(self, method):
        DBSession.remove()
        testing.tearDown()

    def test_passing_view(self):
        request = testing.DummyRequest()
        controller = Controller(request)
        info = controller.user()
        self.assertEqual(info['user'].name, 'admin')


class TestFailure(unittest.TestCase):
    def setup_method(self, method):
        self.config = testing.setUp()
        engine = sqlalchemy.create_engine('sqlite://')
        DBSession.configure(bind=engine)

    def teardown_method(self, method):
        DBSession.remove()
        testing.tearDown()

    def test_failing_view(self):
        request = testing.DummyRequest()
        controller = Controller(request)
        info = controller.user()
        self.assertEqual(info.status_int, 500)
