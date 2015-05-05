from pyramid import httpexceptions
from redis import StrictRedis


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
        if self.request.method == 'POST' and form.validate():
            return True
        if 'csrf_token' in form.errors:
            raise httpexceptions.HTTPUnauthorized()
        return False

    @property
    def redis(self):
        """ :rtype: StrictRedis """
        return self.request.session.redis

    @property
    def user(self):
        """ :rtype: User """
        return self.request.user
