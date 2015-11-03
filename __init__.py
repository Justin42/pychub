import random
import string
import types

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
import mongoengine as mongo
from pyramid.events import subscriber, BeforeRender

from pychub import request_methods
from lodestone.LodestoneClient import LodestoneClient
from model.FreeCompany import FreeCompany
from pychub.request_methods import *
from security import get_groups, RootFactory
from util import fc_from_dict, character_from_dict

renderer_globals = {}


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory='pychub.security.RootFactory')
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path('templates', prepend=True)
    config.set_authentication_policy(AuthTktAuthenticationPolicy(gen_secret(20), callback=get_groups, hashalg='sha512'))
    config.set_authorization_policy(ACLAuthorizationPolicy())

    # Database connect
    mongo.connect(config.registry.settings['mongo_database'])

    # Collect initial data
    try:
        lodestone_id = config.registry.settings['free_company.id']
        free_company = FreeCompany.objects.get(lodestone_id=lodestone_id)
    except DoesNotExist:
        lodestone = LodestoneClient()
        free_company = lodestone.get_fc_by_id(config.registry.settings['free_company.id'])
        lodestone.get_fc_members(free_company)
        free_company = fc_from_dict(free_company)
        free_company.save()
        for name, data in free_company.members.items:
            char = lodestone.get_character_data(data['lodestone_id'], True)
            char = character_from_dict(char)
            char.save()
            break
    renderer_globals['free_company'] = free_company

    # Add request methods dynamically
    for function in dir(request_methods):
        if isinstance(request_methods.__dict__.get(function), types.FunctionType):
            config.add_request_method(request_methods.__dict__.get(function), reify=True)

    # Routing
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('login', '/login')
    config.add_route('session', '/session')
    config.add_route('members', '/members')
    config.add_route('character', '/character/{id}')

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


def gen_secret(length):
    return ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in
        range(length))
