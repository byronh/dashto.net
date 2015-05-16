from dashto import errors
from pyramid import httpexceptions
from pyramid_storage import exceptions as fileexceptions
from redis import StrictRedis


class BaseController:
    def __init__(self, request):
        self.request = request
        self.form_kwargs = dict(
            formdata=self.request.POST,
            meta={'csrf_context': self.request.session}
        )

    def redirect(self, route_name, **kwargs):
        return httpexceptions.HTTPFound(location=self.request.route_url(route_name, **kwargs))

    def validate(self, form):
        if self.request.method == 'POST' and form.validate():
            return True
        if 'csrf_token' in form.errors:
            raise httpexceptions.HTTPUnauthorized()
        return False

    def file_upload(self, file_field, extensions=None, folder=None, randomize=True):
        file = file_field.data
        if file is not None and file != b'':
            if not self.request.storage.file_allowed(file):
                raise errors.InvalidFileError()
            try:
                return self.request.storage.save(file, extensions=extensions, folder=folder, randomize=randomize)
            except fileexceptions.FileNotAllowed:
                raise errors.InvalidFileError()
        return None

    @property
    def params(self):
        """ :rtype: dict """
        return self.request.matchdict

    @property
    def redis(self):
        """ :rtype: StrictRedis """
        return self.request.session.redis

    @property
    def user(self):
        """ :rtype: User """
        return self.request.user
