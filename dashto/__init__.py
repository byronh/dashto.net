from dashto import models
from dashto.auth.resources import RootFactory
from dashto.auth.identity import UserAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_redis_sessions import session_factory_from_settings
from sqlalchemy import engine_from_config


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application. """
    engine = engine_from_config(settings, 'sqlalchemy.')
    models.DBSession.configure(bind=engine)
    models.Base.metadata.bind = engine

    config = Configurator(settings=settings)

    config.set_root_factory(RootFactory)
    config.set_authentication_policy(UserAuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_request_method(UserAuthenticationPolicy.get_user, 'user', reify=True)
    config.set_default_permission('private')

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/', traverse='/')
    config.add_route('login', '/login', traverse='/')
    config.add_route('logout', '/logout', traverse='/')

    config.add_route('campaign', '/campaign/{action}')
    config.add_route('chat', '/chat')

    config.add_route('users_index', '/u', traverse='/users')
    config.add_route('users_create', '/u/new', traverse='/users')
    config.add_route('users_view', '/u/{user_id}', traverse='/users/{user_id}')
    config.add_route('users_edit', '/u/{user_id}/edit', traverse='/users/{user_id}')

    config.scan()
    return config.make_wsgi_app()
