from mongoengine import DoesNotExist, NotUniqueError
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from bs4 import BeautifulSoup
import bbcode

from ..model.forum import Category, Topic, Post


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
    return {'topics': topics, 'category': category}


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
    if 'content' in request.POST and request.has_permission('forum_post_reply'):
        content = BeautifulSoup(request.POST['content'][:5000], 'html.parser').get_text()  # Strip all HTML
        content = bbcode.render_html(content)  # Convert remaining BBCode to HTML
        topic.update(push__posts=Post(user=request.get_user, content=content))
        request.session.flash('New reply posted.')
        return HTTPFound(location=request.route_url('forum_topic', page=page, topic_id=topic.id))
    return {'posts': posts, 'topic': topic, 'page': page}


@view_config(route_name='forum_add_category', renderer='forum/add_category.jinja2', permission='forum_add_category')
def add_category(request):
    if 'name' in request.POST:
        try:
            category = Category()
            category.name = request.POST['name'].strip()
            if 'alias' in request.POST:
                category.link_alias = request.POST['alias'].strip()
            else:
                category.link_alias = category.name
            if 'description' in request.POST:
                category.description = request.POST['description'].strip()
            category.save()
            return HTTPFound(location=request.route_url('forum'))
        except NotUniqueError as ex:
            request.session.flash('A category with that name or alias already exists')
            return {}
    else:
        return {}


@view_config(route_name='forum_new_topic', renderer='forum/new_topic.jinja2', permission='forum_new_topic')
def new_topic(request):  # TODO configurable max chars for title and content
    category = Category.objects.get(id=request.matchdict['category_id'])
    if 'name' in request.POST and 'content' in request.POST:
        content = BeautifulSoup(request.POST['content'][:5000], 'html.parser').get_text()  # Strip all HTML
        print('Post text:', content)
        content = bbcode.render_html(content)  # Convert remaining BBCode to HTML
        print('Post HTML:', content)
        topic = Topic(user=request.get_user, name=request.POST['name'][:100], category=category)
        topic.posts.append(Post(user=request.get_user, content=content))
        topic.save()
        return HTTPFound(location=request.route_url('forum_topic', topic_id=topic.id, page=1))
    return {'category': category}


@view_config(route_name='forum_delete_topic', permission='forum_delete_topic')
def delete_topic(request):
    topic = Topic.objects.get(id=request.matchdict['topic_id'])
    topic.delete()
    request.session.flash("Topic deleted.")
    return HTTPFound(location=request.route_url('forum_category', category_name=topic.category.name))


@view_config(route_name='forum_delete_post', permission='forum_delete_post')
def delete_post(request):
    topic = Topic.objects.get(id=request.matchdict['topic_id'])
    topic.update(pull__posts__id=request.matchdict['post_id'])
    return HTTPFound(location=request.route_url('forum_topic', topic_id=topic.id, page=1))
