from dashto.models import DBSession, User
from pyramid.response import Response
from pyramid.session import check_csrf_token
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError


class WebController:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='dashto:templates/index.html')
    def home(self):
        return {}

    @view_config(route_name='user', renderer='dashto:templates/user.html')
    def user(self):
        try:
            user = DBSession.query(User).filter(User.name == 'admin').first()
            if not user:
                return Response('No users found in database', content_type='text/plain')
            return {'user': user}
        except DBAPIError as e:
            return Response('Database error:\n\n{}'.format(e), content_type='text/plain', status_int=500)

    @view_config(route_name='chat', renderer='dashto:templates/chat.html')
    def chat(self):
        return {}

    @view_config(route_name='login', renderer='dashto:templates/index.html')
    def login(self):
        check_csrf_token(self.request)
        return {}
