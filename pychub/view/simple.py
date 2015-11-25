from datetime import datetime

from mongoengine import DoesNotExist
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.view import view_config
from ..model.user import User, Character
from ..model.news_post import NewsPost


@view_config(route_name='home', renderer='home.jinja2')
def home(request):
    return {'news': NewsPost.objects.order_by('-date')[:10]}


@view_config(route_name='members', renderer='members.jinja2')
def members(request):
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

    return {'character': character}


@view_config(route_name='discord', renderer='discord.jinja2')
def discord(request):
    return {}


@view_config(context=HTTPNotFound, renderer='error/not_found.jinja2')
def not_found(request):
    request.response.status = 404
    return {}
