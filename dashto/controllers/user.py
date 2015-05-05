from dashto import forms
from dashto.auth.permissions import Permissions
from dashto.controllers.base import BaseController
from dashto.models import DBSession, User
from pyramid.view import view_config
from sqlalchemy import exc as sqlexceptions


class UsersController(BaseController):

    @view_config(route_name='users_index', permission=Permissions.VIEW, renderer='users/index.html')
    def view_all(self):
        users = DBSession.query(User).all()
        return {
            'users': users
        }

    @view_config(route_name='users_view', permission=Permissions.VIEW, renderer='simple.html')
    def user_view(self):
        user = self.request.context
        return {
            'title': 'View user {}'.format(user.id),
            'body': user.name
        }

    @view_config(route_name='users_edit', permission=Permissions.EDIT, renderer='simple.html')
    def user_edit(self):
        user = self.request.context
        return {
            'title': 'Edit user {}'.format(user.id),
            'body': user.name
        }

    @view_config(route_name='users_create', permission=Permissions.PUBLIC, renderer='users/new.html')
    def user_create(self):
        form = forms.UserCreateForm(**self.form_kwargs)
        if self.validate(form):
            user = User()
            user.name = form.user_name.data
            user.password = form.user_password.data
            try:
                DBSession.add(user)
                DBSession.flush()
                return self.redirect('home')
            except sqlexceptions.IntegrityError:
                form.user_name.errors.append('User already exists')
        return {'form': form}
