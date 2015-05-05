from dashto.auth.permissions import Permissions
from dashto.models import DBSession, User
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Everyone


class RootFactory(dict):
    __acl__ = [(Allow, 'g:admin', ALL_PERMISSIONS),
               (Allow, Everyone, Permissions.PUBLIC)]

    def __init__(self, request):
        super().__init__()
        self.request = request
        self['users'] = UserFactory(self, 'users')


class UserFactory:
    __acl__ = [(Allow, Everyone, Permissions.VIEW)]

    def __init__(self, parent, name):
        self.__parent__ = parent
        self.__name__ = name

    def __getitem__(self, user_id):
        user = DBSession.query(User).get(user_id)
        if not user:
            raise KeyError
        user.__parent__ = self
        user.__name__ = user_id
        return user
