from enum import Enum
from pyramid.security import Everyone, Authenticated, unauthenticated_userid, Allow, ALL_PERMISSIONS
from dashto.models import DBSession, User


class UserAuthenticationPolicy:

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

    @staticmethod
    def get_user(request):
        user_id = unauthenticated_userid(request)
        if user_id is not None:
            return DBSession.query(User).get(user_id)


class Permissions(Enum):
    PUBLIC = 'public'
    MEMBER = 'member'
    ADMIN = 'admin'


class RootFactory(dict):
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
        (Allow, Everyone, Permissions.PUBLIC),
        (Allow, Authenticated, Permissions.MEMBER),
    ]

    def __init__(self, request):
        super().__init__()
        self.request = request
