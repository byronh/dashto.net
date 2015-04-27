from dashto import forms
from dashto.models import DBSession, User
from pyramid import httpexceptions
from pyramid.view import view_config


class BaseController:
    def __init__(self, request):
        self.request = request
        self.form_kwargs = dict(
            formdata=self.request.POST,
            meta={'csrf_context': self.request.session}
        )

    def redirect(self, route_name):
        return httpexceptions.HTTPFound(location=self.request.route_url(route_name))

    def validate(self, form):
        return self.request.method == 'POST' and form.validate()


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
            if user:
                self.request.session['user'] = user
            return self.redirect('home')
        return {'form': form}


class AdminController(BaseController):
    @view_config(route_name='user', match_param='action=create', renderer='templates/user/create.html')
    def user_create(self):
        form = forms.UserCreateForm(**self.form_kwargs)
        if self.validate(form):
            user = User()
            user.name = form.user_name.data
            user.password = form.user_password.data
            DBSession.add(user)
            return self.redirect('home')
        return {'form': form}
