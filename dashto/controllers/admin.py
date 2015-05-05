from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import User, DBSession
from pyramid.view import view_config
from sqlalchemy import exc as sqlexceptions


class AdminController(BaseController):

    @view_config(route_name='user', match_param='action=new', renderer='user/new.html', permission='create')
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
