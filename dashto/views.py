from dashto import forms
from dashto.models import DBSession, User
from pyramid import httpexceptions
from pyramid.view import view_config
from sqlalchemy import exc as sqlexceptions


class BaseController:
    def __init__(self, request):
        self.request = request
        self.form_kwargs = dict(
            formdata=self.request.POST,
            meta={'csrf_context': self.request.session}
        )
        user_id = self.request.session.get('user_id')
        if user_id:
            self._user = DBSession.query(User).filter(User.id == user_id).first()

    def redirect(self, route_name):
        return httpexceptions.HTTPFound(location=self.request.route_url(route_name))

    def validate(self, form):
        if self.request.method == 'POST' and form.validate():
            return True
        if 'csrf_token' in form.errors:
            raise httpexceptions.HTTPUnauthorized()
        return False

    @property
    def user(self):
        """ :rtype: User """
        return self._user


class MainController(BaseController):
    @view_config(route_name='home', renderer='templates/index.html')
    def home(self):
        form = forms.UserLoginForm(**self.form_kwargs)
        return {'form': form}

    @view_config(route_name='chat', renderer='templates/chat.html')
    def chat(self):
        return {}

    @view_config(route_name='login', renderer='templates/index.html')
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


class AdminController(BaseController):
    @view_config(route_name='user', match_param='action=create', renderer='templates/user/create.html')
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
