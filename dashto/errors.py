import logging
from pyramid import httpexceptions
from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.security import NO_PERMISSION_REQUIRED


class DashtoError(Exception):
    pass


class InvalidFileError(DashtoError):
    pass


def render_error_page(request, error_code, title, body=None):
    request.response.status = error_code
    data = {'title': '{} {}'.format(error_code, title)}
    if body:
        data['body'] = body
    return render_to_response('simple.html', data, request)


def require_login(request):
    query_string = 'from={}'.format(request.path_qs)
    return httpexceptions.HTTPFound(location=request.route_url('login', _query=query_string))


@view_config(context=httpexceptions.HTTPNotFound, permission=NO_PERMISSION_REQUIRED)
def error_not_found(context, request):
    return render_error_page(request, 404, 'not found', 'Where could it have gone?')


@view_config(context=httpexceptions.HTTPBadRequest, permission=NO_PERMISSION_REQUIRED)
def error_bad_request(context, request):
    return render_error_page(request, 400, 'bad request')


@view_config(context=httpexceptions.HTTPForbidden, permission=NO_PERMISSION_REQUIRED)
def error_forbidden(context, request):
    return require_login(request)


@view_config(context=httpexceptions.HTTPUnauthorized, permission=NO_PERMISSION_REQUIRED)
def error_unauthorized(context, request):
    return require_login(request)


@view_config(context=Exception, permission=NO_PERMISSION_REQUIRED)
def error_internal(context, request):
    logging.exception(context)  # Also sends to logstash
    return render_error_page(request, 500, 'critical system failure', 'Looks something something blew up!')
