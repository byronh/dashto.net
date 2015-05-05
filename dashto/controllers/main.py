from dashto import forms
from dashto.controllers.base import BaseController
from dashto.models import DBSession, User
from pyramid.view import view_config


class MainController(BaseController):

    @view_config(route_name='home', renderer='index.html')
    def home(self):
        form = forms.UserLoginForm(**self.form_kwargs)
        return {'form': form}

    @view_config(route_name='login', renderer='index.html')
    def login(self):
        form = forms.UserLoginForm(**self.form_kwargs)
        if self.validate(form):
            user = DBSession.query(User).filter(User.name == form.user_name.data).first()
            if user and user.validate_password(form.user_password.data):
                self.request.session['user_id'] = user.id
                return self.redirect('home')
            else:
                form.user_name.errors.append('Invalid credentials')
        return {'form': form}

    @view_config(route_name='logout')
    def logout(self):
        self.request.session.invalidate()
        return self.redirect('home')