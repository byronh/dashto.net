from dashto.models import DBSession
from dashto.models import User
from pyramid.security import Allow, Everyone, Authenticated
from pyramid.security import unauthenticated_userid


class RootFactory:
    __acl__ = [(Allow, Everyone, 'public'),
               (Allow, Authenticated, 'view'),
               (Allow, Authenticated, 'create'),
               (Allow, Authenticated, 'edit'), ]

    def __init__(self, request):
        self.request = request


class AuthenticationPolicy:

    def unauthenticated_userid(self, request):
        return request.session.get('user_id')

    def authenticated_userid(self, request):
        if request.user:
            return request.user.id

    def effective_principals(self, request):
        principals = [Everyone]
        user = request.user
        if user:
            principals += [Authenticated, 'u:%s' % user.id]
            # principals.extend(('g:%s' % g.name for g in user.groups))
        return principals


def get_user(request):
    user_id = unauthenticated_userid(request)
    if user_id is not None:
        return DBSession.query(User).get(user_id)
