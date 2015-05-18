from dashto import forms
from dashto.auth import Permissions
from dashto.controllers.base import BaseController
from dashto.models import DBSession
from dashto.models import Character, User
from pyramid import httpexceptions
from pyramid.view import view_config
from sqlalchemy import exc as sqlexceptions


class UsersController(BaseController):

    def get_user(self):
        """ :rtype: User """
        user_id = self.params['user_id']
        if user_id == str(self.user.id):
            return self.user
        user = DBSession.query(User).get(user_id)
        if not user:
            raise httpexceptions.HTTPNotFound()
        return user

    @view_config(route_name='users_index', renderer='users/index.html')
    def view_all(self):
        users = DBSession.query(User).order_by(User.name).all()
        return {'users': users}

    @view_config(route_name='users_view', renderer='users/view.html')
    def view(self):
        user = self.get_user()
        characters = DBSession.query(Character).filter(Character.user == user).all()
        return {'user': user, 'characters': characters}

    @view_config(route_name='users_edit', renderer='simple.html')
    def edit(self):
        user = self.get_user()
        if user != self.user:
            raise httpexceptions.HTTPForbidden()
        return {
            'title': 'Edit user {}'.format(user.id),
            'body': user.name
        }

    @view_config(route_name='users_create', renderer='users/new.html', permission=Permissions.ADMIN)
    def create(self):
        form = forms.UserCreateForm(**self.form_kwargs)
        if self.validate(form):
            user = User()
            user.name = form.user_name.data
            user.password = form.user_password.data
            try:
                DBSession.add(user)
                DBSession.flush()
                return self.redirect('users_index')
            except sqlexceptions.IntegrityError:
                form.user_name.errors.append('User already exists')
        return {'form': form}
