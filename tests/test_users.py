import unittest
import sqlalchemy
import transaction
from dashto.models import Base, DBSession, User
from dashto.views import WebController
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
        controller = WebController(request)
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
        controller = WebController(request)
        info = controller.user()
        self.assertEqual(info.status_int, 500)
