from dashto import auth, models
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

    config.set_root_factory(auth.RootFactory)
    config.set_authentication_policy(auth.AuthenticationPolicy())
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.add_request_method(auth.get_user, 'user', reify=True)
    config.set_default_permission('public')

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')

    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('campaign', '/campaign/{action}')
    config.add_route('user', '/user/{action}')
    config.add_route('chat', '/chat')

    config.scan()
    return config.make_wsgi_app()
