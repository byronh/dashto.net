from dashto import forms
from dashto.auth import Permissions
from dashto.controllers.base import BaseController
from dashto.models import DBSession, User
from pyramid.view import view_config
from sqlalchemy.orm import undefer


class MainController(BaseController):

    @view_config(route_name='home', permission=Permissions.PUBLIC, renderer='index.html')
    def home(self):
        raise Exception('Test exception')
        return {}

    @view_config(route_name='login', permission=Permissions.PUBLIC, renderer='login.html')
    def login(self):
        form = forms.UserLoginForm(**self.form_kwargs)
        if self.validate(form):
            query = DBSession.query(User).options(undefer('password'))
            user = query.filter(User.name == form.user_name.data).first()
            if user and user.validate_password(form.user_password.data):
                self.request.session['user_id'] = user.id
                destination = self.params.get('from', 'campaigns_index')
                return self.redirect(destination)
            else:
                form.user_name.errors.append('Invalid credentials')
        return {'form': form}

    @view_config(route_name='logout', permission=Permissions.PUBLIC)
    def logout(self):
        self.request.session.invalidate()
        return self.redirect('home')
