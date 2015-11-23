import time
import types

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import subscriber, BeforeRender
from pyramid.session import SignedCookieSessionFactory

from . import request_methods
from .model.free_company import FreeCompany
from .model.user import Character
from .security import get_groups
from .util import gen_random, lodestone
import mongoengine as mongo

renderer_globals = {}


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory='pychub.security.RootFactory')
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path('templates', prepend=True)
    config.set_authentication_policy(AuthTktAuthenticationPolicy(gen_random(20), callback=get_groups, hashalg='sha512'))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_session_factory(SignedCookieSessionFactory(gen_random(20)))

    # Database connect
    mongo.connect(config.registry.settings['mongo_database'])

    # Collect initial data
    try:
        lodestone_id = config.registry.settings['free_company.id']
        free_company = FreeCompany.objects.get(lodestone_id=lodestone_id)
    except mongo.DoesNotExist:
        free_company = lodestone.get_fc_by_id(config.registry.settings['free_company.id'])
        lodestone.get_fc_members(free_company)
        free_company = FreeCompany.from_dict(free_company)
        free_company.save()

    for name, data in free_company.members.items():
        try:
            Character.objects.get(lodestone_id=data['lodestone_id'])
        except mongo.DoesNotExist:
            print('Updating character data for', name)
            char = lodestone.get_character_data(data['lodestone_id'], True)
            char = Character.from_dict(char)
            char.save()
            time.sleep(1) # Slight delay between character data

    renderer_globals['free_company'] = free_company

    # Add request methods dynamically
    for function in dir(request_methods):
        if isinstance(request_methods.__dict__.get(function), types.FunctionType):
            config.add_request_method(request_methods.__dict__.get(function), reify=True)

    # Routing
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('session', '/session')
    config.add_route('members', '/members')
    config.add_route('character', '/character/{id}')

    # Account
    config.add_route('login', '/login')
    config.add_route('register', '/register')
    config.add_route('account', '/account')
    config.add_route('account_add_character', '/account/character/add')

    # Forum
    config.add_route('forum', '/forum')
    config.add_route('forum_category', '/forum/{category_name}')
    config.add_route('forum_topic', '/forum/topic/{topic_id}/{page}')

    # Admin routes
    config.add_route('post_news', '/post_news')
    config.add_route('admin', '/admin')
    config.add_route('admin_view_model', '/admin/{model}')
    config.add_route('admin_delete_item', '/admin/{model}/delete/{id}')
    config.add_route('admin_add_item', '/admin/{model}/add')

    config.scan()

    return config.make_wsgi_app()


@subscriber(BeforeRender)
def add_renderer_globals(event):
    for key, value in renderer_globals.items():
        event[key] = value



