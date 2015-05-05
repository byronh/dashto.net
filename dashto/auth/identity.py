from dashto.models import DBSession, User
from pyramid.security import Everyone, Authenticated
from pyramid.security import unauthenticated_userid


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
