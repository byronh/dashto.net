from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession, User
from pyramid.view import view_config
from sqlalchemy import exc as sqlexceptions


class UsersController(BaseController):

    @view_config(route_name='users_index', renderer='users/index.html')
    def view_all(self):
        users = DBSession.query(User).all()
        return {'users': users}

    @view_config(route_name='users_view', renderer='simple.html')
    def view(self):
        user = DBSession.query(User).get(self.params['user_id'])
        return {
            'title': 'View user {}'.format(user.id),
            'body': user.name
        }

    @view_config(route_name='users_edit', renderer='simple.html')
    def edit(self):
        user = DBSession.query(User).get(self.params['user_id'])
        return {
            'title': 'Edit user {}'.format(user.id),
            'body': user.name
        }

    @view_config(route_name='users_create', renderer='users/new.html')
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
