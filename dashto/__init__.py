from dashto import models
from dashto.auth import Permissions, RootFactory, UserAuthenticationPolicy
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
    config.set_default_permission(Permissions.MEMBER)

    session_factory = session_factory_from_settings(settings)
    config.set_session_factory(session_factory)

    config.add_renderer('.html', 'pyramid_jinja2.renderer_factory')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')

    config.add_route('campaigns_index', '/campaigns')
    config.add_route('campaigns_create', '/campaigns/new')
    config.add_route('campaigns_view', '/campaigns/{campaign_id:\d+}')
    config.add_route('campaigns_play', '/campaigns/{campaign_id:\d+}/play')
    
    config.add_route('characters_index', '/characters')
    config.add_route('characters_create', '/characters/new')
    config.add_route('characters_view', '/characters/{character_id:\d+}')

    config.add_route('users_index', '/users')
    config.add_route('users_create', '/users/new')
    config.add_route('users_view', '/users/{user_id:\d+}')
    config.add_route('users_edit', '/users/{user_id:\d+}/edit')

    config.scan()
    return config.make_wsgi_app()
