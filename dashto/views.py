from dashto.db import DBSession
from dashto.models import User
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError


class Controller:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='templates/index.html')
    def index(self):
        return {}

    @view_config(route_name='user', renderer='templates/user.html')
    def user(self):
        try:
            user = DBSession.query(User).filter(User.name == 'admin').first()
            if not user:
                return Response('No users found in database', content_type='text/plain')
            return {'user': user}
        except DBAPIError as e:
            return Response('Database error:\n\n{}'.format(e), content_type='text/plain', status_int=500)

    @view_config(route_name='chat', renderer='templates/chat.html')
    def chat(self):
        return {}
