from datetime import datetime

from mongoengine import DoesNotExist
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config

from ..model.free_company import FreeCompany
from ..model import common
from ..model.common import update_service
from ..util import copy_keys
from ..model.user import User, Character
from ..model.news_post import NewsPost


@view_config(route_name='home', renderer='home.jinja2')
def home(request):
    return {'news': NewsPost.objects.order_by('-date')[:10]}


@view_config(route_name='members', renderer='members.jinja2')
def members(request):
    try:
        free_company = FreeCompany.objects.get(lodestone_id=request.registry.settings['free_company.id'])
        update_service.queue(free_company)
    except DoesNotExist:
        pass
    return {}


@view_config(route_name='post_news', renderer='post_news.jinja2', permission='post_news')
def post_news(request):
    if 'body' in request.POST:
        news_post = NewsPost()
        news_post.user = User.objects.get(username=request.authenticated_userid)
        news_post.body = request.POST['body']
        news_post.title = request.POST['title']
        news_post.date = datetime.now()
        news_post.save()
        return HTTPFound(location=request.route_url('home'))
    else:
        return {}


@view_config(route_name='character', renderer='character.jinja2')
def view_character(request):
    try:
        character = Character.objects.get(lodestone_id=request.matchdict['id'])
    except DoesNotExist:
        return HTTPNotFound()

    classes = character.class_dict

    war_classes = copy_keys(classes, common.war_classes)
    magic_classes = copy_keys(classes, common.magic_classes)
    hand_classes = copy_keys(classes, common.hand_classes)
    land_classes = copy_keys(classes, common.land_classes)
    extra_classes = copy_keys(classes, common.extra_classes)

    update_service.queue(character)
    return {'character': character, 'war_classes': war_classes, 'hand_classes': hand_classes,
            'magic_classes': magic_classes, 'land_classes': land_classes, 'extra_classes': extra_classes}


@view_config(route_name='discord', renderer='discord.jinja2')
def discord(request):
    return {'discord_url': request.registry.settings['discord_url']}


@view_config(context=HTTPNotFound, renderer='error/not_found.jinja2')
def not_found(request):
    request.response.status = 404
    return {}
