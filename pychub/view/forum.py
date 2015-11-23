from mongoengine import DoesNotExist
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from ..model.forum import Category, Topic


@view_config(route_name='forum', renderer='forum/index.jinja2')
def index(request):
    return {'categories': Category.objects}


@view_config(route_name='forum_category', renderer='forum/category.jinja2')
def category_view(request): # TODO Paginate topics
    try:
        category = Category.objects.get(name=request.matchdict['category_name'])
    except DoesNotExist:
        try:
            category = Category.objects.get(link_alias=request.matchdict['category_name'])
        except DoesNotExist:
            request.session.flash("Invalid category.")
            return HTTPFound(location=request.route_url('forum'))
    topics = Topic.objects(category=category)
    return {'topics': topics}


@view_config(route_name='forum_topic', renderer='forum/topic.jinja2')
def topic_view(request):
    posts_per_page = 20  # TODO Posts per page should probably be configurable
    page = int(request.matchdict['page'])
    start = (page-1) * posts_per_page
    end = posts_per_page * page

    try:
        topic = Topic.objects.get(id=request.matchdict['topic_id'])
        posts = topic.posts[start:end]
    except DoesNotExist:
        request.session.flash("Invalid topic ID")
        return HTTPFound(location=request.route_url('forum'))
    return {'posts': posts, 'topic': topic}
